import json
import os
import traceback
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Order
from schemas import CheckoutRequest, CheckoutSessionResponse
from email_service import send_order_confirmation, send_seller_notification

router = APIRouter(prefix="/api/payments", tags=["payments"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.post("/test-email")
async def test_email():
    import resend as _resend
    _resend.api_key = os.getenv("RESEND_API_KEY", "")
    try:
        r = _resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": os.getenv("SELLER_EMAIL", "minhhoangle2909@gmail.com"),
            "subject": "🧪 Test email backend Render",
            "html": "<p>Email envoyé depuis Render. Resend key: " + os.getenv("RESEND_API_KEY","?")[:8] + "...</p>",
        })
        return {"ok": True, "id": r.get("id")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(body: CheckoutRequest):
    if not body.items:
        raise HTTPException(status_code=400, detail="Le panier est vide.")

    if not stripe.api_key or stripe.api_key == "sk_test_REPLACE_ME":
        raise HTTPException(
            status_code=503,
            detail="Paiement indisponible — clé Stripe non configurée.",
        )

    line_items = [
        {
            "price_data": {
                "currency": "eur",
                "unit_amount": int(round(item.price * 100)),
                "product_data": {
                    "name": f"{item.name} — {item.size} / {item.color}",
                },
            },
            "quantity": item.quantity,
        }
        for item in body.items
    ]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=body.email,
            line_items=line_items,
            mode="payment",
            success_url=f"{FRONTEND_URL}/success?ref={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/cart",
            billing_address_collection="required",
            shipping_address_collection={"allowed_countries": ["FR", "BE", "CH", "LU"]},
            metadata={"buyer_email": body.email},
        )
    except stripe.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Stripe error: {str(exc)}")

    return CheckoutSessionResponse(session_id=session.id, url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, Exception) as exc:
        err_msg = str(exc)
        if "signature" in err_msg.lower() or "timestamp" in err_msg.lower():
            raise HTTPException(status_code=400, detail="Signature webhook invalide")
        raise HTTPException(status_code=400, detail=f"Webhook error: {err_msg}")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        try:
            await _handle_checkout_completed(session_obj, db)
        except Exception:
            print(f"[webhook] ERROR:\n{traceback.format_exc()}")

    return {"received": True}


async def _handle_checkout_completed(session: dict, db: AsyncSession) -> None:
    import resend as _resend
    _resend.api_key = os.getenv("RESEND_API_KEY", "")

    stripe_payment_id = session["id"]
    customer_details = session.get("customer_details") or {}
    buyer_email = customer_details.get("email") or (session.get("metadata") or {}).get("buyer_email", "")
    seller_email = os.getenv("SELLER_EMAIL", "minhhoangle2909@gmail.com")

    from sqlalchemy import select
    existing = await db.execute(select(Order).where(Order.stripe_payment_id == stripe_payment_id))
    if existing.scalar_one_or_none():
        print(f"[webhook] Order {stripe_payment_id} already exists, skipping")
        return

    # Build order items
    try:
        line_items_resp = stripe.checkout.Session.list_line_items(stripe_payment_id, limit=100)
        order_items = []
        total = 0.0
        for li in line_items_resp.data:
            unit_price = round((li.price.unit_amount or 0) / 100, 2)
            qty = li.quantity or 1
            subtotal = round(unit_price * qty, 2)
            total += subtotal
            order_items.append({
                "product_name": li.description or "Produit",
                "quantity": qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })
    except Exception as e:
        print(f"[webhook] list_line_items failed: {e}")
        amount_total = session.get("amount_total") or 0
        total = round(amount_total / 100, 2)
        order_items = [{"product_name": "Commande", "quantity": 1, "unit_price": total, "subtotal": total}]

    print(f"[webhook] Processing order: buyer={buyer_email}, total={total}, items={len(order_items)}")

    # Save order
    order_id_str = stripe_payment_id[-8:].upper()
    try:
        order = Order(
            user_id=None,
            email=buyer_email or seller_email,
            items_json=json.dumps(order_items),
            total_amount=round(total, 2),
            stripe_payment_id=stripe_payment_id,
            status="paid",
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        order_id_str = str(order.id)
        print(f"[webhook] Order saved: id={order_id_str}")
    except Exception as e:
        print(f"[webhook] DB error: {e}")
        await db.rollback()

    # Send seller notification (always to verified email)
    try:
        _resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": seller_email,
            "subject": f"🛍 Nouvelle commande #{order_id_str} — {total:.2f}€",
            "html": build_seller_html(buyer_email, order_id_str, order_items, total),
        })
        print(f"[webhook] Seller email sent to {seller_email}")
    except Exception as e:
        print(f"[webhook] Seller email failed: {e}")

    # Send buyer confirmation (may fail on Resend free tier if not verified)
    if buyer_email and buyer_email != seller_email:
        try:
            _resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": buyer_email,
                "subject": f"Commande #{order_id_str} confirmée ✓",
                "html": build_buyer_html(buyer_email, order_id_str, order_items, total),
            })
            print(f"[webhook] Buyer email sent to {buyer_email}")
        except Exception as e:
            print(f"[webhook] Buyer email failed (free tier?): {e}")


def build_seller_html(buyer_email: str, order_id: str, items: list, total: float) -> str:
    rows = "".join(
        f"<tr><td style='padding:8px'>{i.get('product_name','?')}</td>"
        f"<td style='padding:8px;text-align:center'>{i.get('quantity',1)}</td>"
        f"<td style='padding:8px;text-align:right'>{i.get('subtotal',0):.2f}€</td></tr>"
        for i in items
    )
    return f"""<div style="font-family:Arial;max-width:600px;margin:0 auto">
<div style="background:#dc2626;padding:20px;text-align:center">
  <h1 style="color:#fff;margin:0">🛍 Nouvelle commande #{order_id}</h1>
</div>
<div style="padding:20px">
  <p><b>Client :</b> {buyer_email}</p>
  <table style="width:100%;border-collapse:collapse">
    <tr style="background:#f5f5f5"><th style="padding:8px;text-align:left">Produit</th><th>Qté</th><th>Total</th></tr>
    {rows}
  </table>
  <p style="text-align:right;font-size:18px;border-top:2px solid #dc2626;padding-top:10px">
    <b>Total : {total:.2f}€</b>
  </p>
</div></div>"""


def build_buyer_html(buyer_email: str, order_id: str, items: list, total: float) -> str:
    rows = "".join(
        f"<tr><td style='padding:8px'>{i.get('product_name','?')}</td>"
        f"<td style='padding:8px;text-align:center'>{i.get('quantity',1)}</td>"
        f"<td style='padding:8px;text-align:right'>{i.get('subtotal',0):.2f}€</td></tr>"
        for i in items
    )
    return f"""<div style="font-family:Arial;max-width:600px;margin:0 auto">
<div style="background:#1a1a1a;padding:20px;text-align:center">
  <h1 style="color:#fff;margin:0">Commande confirmée ✓</h1>
</div>
<div style="padding:20px">
  <p>Merci pour votre commande ! Référence : <b>#{order_id}</b></p>
  <table style="width:100%;border-collapse:collapse">
    <tr style="background:#f5f5f5"><th style="padding:8px;text-align:left">Produit</th><th>Qté</th><th>Total</th></tr>
    {rows}
  </table>
  <p style="text-align:right;font-size:18px;border-top:2px solid #222;padding-top:10px">
    <b>Total : {total:.2f}€</b>
  </p>
  <div style="background:#f0f9ff;padding:12px;border-radius:6px;margin-top:16px">
    📦 Livraison estimée : 2–3 jours ouvrés en France
  </div>
</div></div>"""
