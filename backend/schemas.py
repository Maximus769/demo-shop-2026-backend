from datetime import datetime
from typing import Any
from pydantic import BaseModel, EmailStr, Field


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenIn(BaseModel):
    refresh_token: str


# ─── Products ─────────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    image_url: str | None
    sizes: list[str]
    colors: list[str]
    stock: int
    is_active: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_product(cls, p: Any) -> "ProductOut":
        return cls(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            image_url=p.image_url,
            sizes=p.sizes,
            colors=p.colors,
            stock=p.stock,
            is_active=p.is_active,
        )


# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)
    size: str = Field(min_length=1, max_length=10)
    color: str = Field(min_length=1, max_length=50)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    size: str
    color: str
    product: ProductOut | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_item(cls, item: Any) -> "CartItemOut":
        product_out = None
        if item.product:
            product_out = ProductOut.from_orm_product(item.product)
        return cls(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            size=item.size,
            color=item.color,
            product=product_out,
        )


# ─── Orders ───────────────────────────────────────────────────────────────────

class OrderItemSchema(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    size: str
    color: str
    unit_price: float
    subtotal: float


class OrderCreate(BaseModel):
    email: EmailStr
    stripe_payment_id: str | None = None


class OrderOut(BaseModel):
    id: int
    email: str
    items: list[dict]
    total_amount: float
    stripe_payment_id: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_order(cls, o: Any) -> "OrderOut":
        return cls(
            id=o.id,
            email=o.email,
            items=o.items,
            total_amount=o.total_amount,
            stripe_payment_id=o.stripe_payment_id,
            status=o.status,
            created_at=o.created_at,
        )


# ─── Payments ─────────────────────────────────────────────────────────────────

class CheckoutItem(BaseModel):
    name: str
    price: float = Field(gt=0)  # euros
    quantity: int = Field(ge=1, le=99)
    size: str
    color: str


class CheckoutRequest(BaseModel):
    email: EmailStr
    items: list[CheckoutItem]


class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str
