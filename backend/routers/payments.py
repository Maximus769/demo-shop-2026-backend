import json
import os
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
    except stripe.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Signature webhook invalide")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(exc)}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await _handle_checkout_completed(session, db)

    return {"received": True}


async def _handle_checkout_completed(session: dict, db: AsyncSession) -> None:
    stripe_payment_id = session["id"]
    buyer_email = session.get("customer_details", {}).get("email", "") or session.get("metadata", {}).get("buyer_email", "")

    from sqlalchemy import select
    existing = await db.execute(select(Order).where(Order.stripe_payment_id == stripe_payment_id))
    if existing.scalar_one_or_none():
        return

    line_items_resp = stripe.checkout.Session.list_line_items(stripe_payment_id, limit=100)
    order_items = []
    total = 0.0
    for li in line_items_resp.data:
        unit_price = li.price.unit_amount / 100
        qty = li.quantity
        subtotal = round(unit_price * qty, 2)
        total += subtotal
        order_items.append({
            "product_name": li.description,
            "quantity": qty,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    order = Order(
        user_id=None,
        email=buyer_email,
        items_json=json.dumps(order_items),
        total_amount=round(total, 2),
        stripe_payment_id=stripe_payment_id,
        status="paid",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    send_order_confirmation(buyer_email, str(order.id), order_items, total)
    send_seller_notification(buyer_email, str(order.id), order_items, total)
