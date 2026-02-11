import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.base import BaseSchema

# --- Restaurant ---


class RestaurantCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class RestaurantUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class RestaurantResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    group_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RestaurantDetailResponse(RestaurantResponse):
    dishes: list["DishResponse"] = []


# --- Dish ---


class DishCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    detail: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(ge=0, decimal_places=2)


class DishUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    detail: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)


class DishResponse(BaseSchema):
    id: uuid.UUID
    name: str
    detail: str | None
    price: Decimal
    restaurant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
