import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.base import BaseSchema

# --- Order ---


class OrderCreate(BaseSchema):
    restaurant_id: uuid.UUID | None = None
    restaurant_name: str | None = Field(default=None, max_length=255)


class OrderUpdateStatus(BaseSchema):
    status: str


class OrderSetDeliveryFee(BaseSchema):
    """Set delivery/packing fee. Either total (divided equally) or per_person."""

    delivery_fee_total: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    delivery_fee_per_person: Decimal | None = Field(default=None, ge=0, decimal_places=2)


class OrderResponse(BaseSchema):
    id: uuid.UUID
    group_id: uuid.UUID
    restaurant_id: uuid.UUID | None
    restaurant_name: str | None
    initiator_id: uuid.UUID
    status: str
    delivery_fee_total: Decimal | None
    delivery_fee_per_person: Decimal | None
    created_at: datetime
    updated_at: datetime


class OrderDetailResponse(OrderResponse):
    items: list["OrderItemResponse"] = []
    initiator_name: str | None = None
    participant_count: int = 0
    total_amount: Decimal = Decimal("0.00")


# --- Order Item ---


class OrderItemCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    detail: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(ge=0, decimal_places=2)
    dish_id: uuid.UUID | None = None


class OrderItemUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    detail: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)


class OrderItemResponse(BaseSchema):
    id: uuid.UUID
    order_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    detail: str | None
    price: Decimal
    dish_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    user_full_name: str | None = None


# --- Favorite Dish ---


class FavoriteDishResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    dish_id: uuid.UUID
    dish_name: str | None = None
    dish_detail: str | None = None
    dish_price: Decimal | None = None
    restaurant_id: uuid.UUID | None = None
