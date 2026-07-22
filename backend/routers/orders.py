import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import CartItem, Order, Product, User
from schemas import OrderCreate, OrderOut
from auth import get_current_user, get_required_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    body: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if user:
        stmt = (
            select(CartItem)
            .where(CartItem.user_id == user.id)
            .options(selectinload(CartItem.product))
        )
    else:
        raise HTTPException(status_code=400, detail="Utilisateur requis pour créer une commande.")

    result = await db.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Le panier est vide.")

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
        user_id=user.id if user else None,
        email=body.email,
        items_json=json.dumps(order_items),
        total_amount=round(total, 2),
        stripe_payment_id=body.stripe_payment_id,
        status="pending",
    )
    db.add(order)
    await db.flush()

    for item in cart_items:
        await db.delete(item)

    await db.refresh(order)
    return OrderOut.from_orm_order(order)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_required_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return OrderOut.from_orm_order(order)


@router.get("", response_model=list[OrderOut])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_required_user),
):
    result = await db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    return [OrderOut.from_orm_order(o) for o in orders]
