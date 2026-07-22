import uuid
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import CartItem, Product, User
from schemas import CartItemIn, CartItemOut, CartItemUpdate
from auth import get_current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])

SESSION_COOKIE = "shop_session"


def _get_session_id(session_id: str | None) -> str:
    return session_id or str(uuid.uuid4())


async def _get_cart_query(db: AsyncSession, user: User | None, session_id: str):
    if user:
        stmt = (
            select(CartItem)
            .where(CartItem.user_id == user.id)
            .options(selectinload(CartItem.product))
        )
    else:
        stmt = (
            select(CartItem)
            .where(CartItem.session_id == session_id, CartItem.user_id.is_(None))
            .options(selectinload(CartItem.product))
        )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("", response_model=list[CartItemOut])
async def get_cart(
    response: Response,
    shop_session: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    session_id = _get_session_id(shop_session)
    if not shop_session:
        response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30)

    items = await _get_cart_query(db, user, session_id)
    return [CartItemOut.from_orm_item(i) for i in items]


@router.post("", response_model=CartItemOut, status_code=201)
async def add_to_cart(
    body: CartItemIn,
    response: Response,
    shop_session: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    session_id = _get_session_id(shop_session)
    if not shop_session:
        response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30)

    product_result = await db.execute(select(Product).where(Product.id == body.product_id, Product.is_active == True))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    if body.size not in product.sizes:
        raise HTTPException(status_code=400, detail=f"Taille invalide. Options: {product.sizes}")
    if body.color not in product.colors:
        raise HTTPException(status_code=400, detail=f"Couleur invalide. Options: {product.colors}")

    # merge if identical item exists
    if user:
        stmt = select(CartItem).where(
            CartItem.user_id == user.id,
            CartItem.product_id == body.product_id,
            CartItem.size == body.size,
            CartItem.color == body.color,
        )
    else:
        stmt = select(CartItem).where(
            CartItem.session_id == session_id,
            CartItem.user_id.is_(None),
            CartItem.product_id == body.product_id,
            CartItem.size == body.size,
            CartItem.color == body.color,
        )
    existing_result = await db.execute(stmt)
    existing = existing_result.scalar_one_or_none()

    if existing:
        existing.quantity = min(existing.quantity + body.quantity, 99)
        await db.flush()
        await db.refresh(existing, ["product"])
        return CartItemOut.from_orm_item(existing)

    cart_item = CartItem(
        user_id=user.id if user else None,
        session_id=None if user else session_id,
        product_id=body.product_id,
        quantity=body.quantity,
        size=body.size,
        color=body.color,
    )
    db.add(cart_item)
    await db.flush()

    result = await db.execute(
        select(CartItem).where(CartItem.id == cart_item.id).options(selectinload(CartItem.product))
    )
    item_with_product = result.scalar_one()
    return CartItemOut.from_orm_item(item_with_product)


@router.put("/{item_id}", response_model=CartItemOut)
async def update_cart_item(
    item_id: int,
    body: CartItemUpdate,
    shop_session: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id).options(selectinload(CartItem.product))
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Article introuvable")

    if user and item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    if not user and item.session_id != shop_session:
        raise HTTPException(status_code=403, detail="Accès refusé")

    item.quantity = body.quantity
    await db.flush()
    return CartItemOut.from_orm_item(item)


@router.delete("/{item_id}", status_code=204)
async def remove_cart_item(
    item_id: int,
    shop_session: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Article introuvable")

    if user and item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    if not user and item.session_id != shop_session:
        raise HTTPException(status_code=403, detail="Accès refusé")

    await db.delete(item)


@router.delete("", status_code=204)
async def clear_cart(
    shop_session: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if user:
        result = await db.execute(select(CartItem).where(CartItem.user_id == user.id))
    else:
        if not shop_session:
            return
        result = await db.execute(
            select(CartItem).where(CartItem.session_id == shop_session, CartItem.user_id.is_(None))
        )
    items = result.scalars().all()
    for item in items:
        await db.delete(item)
