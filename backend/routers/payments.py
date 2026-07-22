import json
import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import CartItem, Order, Product, User
from schemas import CheckoutSessionResponse
from auth import get_current_user
from email_service import send_order_confirmation, send_seller_notification

router = APIRouter(prefix="/api/payments", tags=["payments"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    session_cookie = request.cookies.get("shop_session")

    if user:
        stmt = (
            select(CartItem)
            .where(CartItem.user_id == user.id)
            .options(selectinload(CartItem.product))
        )
    elif session_cookie:
        stmt = (
            select(CartItem)
            .where(CartItem.session_id == session_cookie, CartItem.user_id.is_(None))
            .options(selectinload(CartItem.product))
        )
    else:
        raise HTTPException(status_code=400, detail="Panier vide ou session introuvable.")

    result = await db.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Le panier est vide.")

    line_items = []
    for item in cart_items:
        product: Product = item.product
        line_items.append({
            "price_data": {
                "currency": "eur",
                "unit_amount": int(product.price * 100),
                "product_data": {
                    "name": f"{product.name} — {item.size} / {item.color}",
                    "description": product.description or "",
                    "images": [product.image_url] if product.image_url else [],
                },
            },
            "quantity": item.quantity,
        })

    metadata = {
        "user_id": str(user.id) if user else "",
        "session_id": session_cookie or "",
    }

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{FRONTEND_URL}/success?ref={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/cart",
            metadata=metadata,
            billing_address_collection="required",
            shipping_address_collection={"allowed_countries": ["FR", "BE", "CH", "LU"]},
        )
    except stripe.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Stripe error: {str(exc)}")

    return CheckoutSessionResponse(session_id=checkout_session.id, url=checkout_session.url)


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
    buyer_email = session.get("customer_details", {}).get("email", "")
    metadata = session.get("metadata", {})
    user_id_str = metadata.get("user_id", "")
    session_id = metadata.get("session_id", "")

    existing_result = await db.execute(
        select(Order).where(Order.stripe_payment_id == stripe_payment_id)
    )
    if existing_result.scalar_one_or_none():
        return

    user_id: int | None = int(user_id_str) if user_id_str else None

    if user_id:
        stmt = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))
        )
    elif session_id:
        stmt = (
            select(CartItem)
            .where(CartItem.session_id == session_id, CartItem.user_id.is_(None))
            .options(selectinload(CartItem.product))
        )
    else:
        return

    result = await db.execute(stmt)
    cart_items = result.scalars().all()

    order_items = []
    total = 0.0
    for item in cart_items:
        product: Product = item.product
        subtotal = round(product.price * item.quantity, 2)
        total += subtotal
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "size": item.size,
            "color": item.color,
            "unit_price": product.price,
            "subtotal": subtotal,
        })

    order = Order(
        user_id=user_id,
        email=buyer_email,
        items_json=json.dumps(order_items),
        total_amount=round(total, 2),
        stripe_payment_id=stripe_payment_id,
        status="paid",
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)

    for item in cart_items:
        await db.delete(item)

    await db.commit()

    order_id_str = str(order.id)
    send_order_confirmation(buyer_email, order_id_str, order_items, total)
    send_seller_notification(buyer_email, order_id_str, order_items, total)
