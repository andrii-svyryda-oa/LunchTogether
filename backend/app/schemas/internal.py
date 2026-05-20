"""Internal Pydantic schemas used by repositories and workflows.

These are not exposed via the API. They represent the exact data shapes
needed when creating or updating database records.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from app.models.enums import BalanceChangeType, InvitationStatus, OrderStatus, UserRole
from app.schemas.base import BaseSchema

# --- User ---


class UserInternalCreate(BaseSchema):
    email: str
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False


class UserPasswordUpdate(BaseSchema):
    hashed_password: str


# --- Password Reset Token ---


class PasswordResetTokenInternalCreate(BaseSchema):
    user_id: uuid.UUID
    token: str
    expires_at: datetime
    used: bool = False


class PasswordResetTokenMarkUsed(BaseSchema):
    used: bool = True


# --- Group ---


class GroupInternalCreate(BaseSchema):
    name: str
    description: str | None = None
    owner_id: uuid.UUID


class GroupLogoUpdate(BaseSchema):
    logo_path: str | None = None


# --- Group Member ---


class GroupMemberInternalCreate(BaseSchema):
    user_id: uuid.UUID
    group_id: uuid.UUID


# --- Group Invitation ---


class GroupInvitationInternalCreate(BaseSchema):
    group_id: uuid.UUID
    inviter_id: uuid.UUID
    invitee_email: str
    invitee_id: uuid.UUID | None = None
    status: InvitationStatus
    token: str


class GroupInvitationStatusUpdate(BaseSchema):
    status: InvitationStatus


# --- Restaurant ---


class RestaurantInternalCreate(BaseSchema):
    name: str
    description: str | None = None
    menu_url: str | None = None
    group_id: uuid.UUID


# --- Dish ---


class DishInternalCreate(BaseSchema):
    name: str
    detail: str | None = None
    price: Decimal
    restaurant_id: uuid.UUID


# --- Order ---


class OrderInternalCreate(BaseSchema):
    group_id: uuid.UUID
    initiator_id: uuid.UUID
    restaurant_id: uuid.UUID | None = None
    restaurant_name: str | None = None
    status: OrderStatus


class OrderStatusInternalUpdate(BaseSchema):
    status: str


class OrderDeliveryFeeInternalUpdate(BaseSchema):
    delivery_fee_total: Decimal | None = None
    delivery_fee_per_person: Decimal | None = None


# --- Order Item ---


class OrderItemInternalCreate(BaseSchema):
    order_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    detail: str | None = None
    price: Decimal
    dish_id: uuid.UUID | None = None
    quantity: int = 1


# --- Favorite Dish ---


class FavoriteDishInternalCreate(BaseSchema):
    user_id: uuid.UUID
    dish_id: uuid.UUID
    is_favorite: bool = True


class FavoriteDishStatusUpdate(BaseSchema):
    is_favorite: bool


# --- Balance ---


class BalanceInternalCreate(BaseSchema):
    user_id: uuid.UUID
    group_id: uuid.UUID
    amount: Decimal = Decimal("0.00")


class BalanceAmountUpdate(BaseSchema):
    amount: Decimal


# --- Balance History ---


class BalanceHistoryInternalCreate(BaseSchema):
    balance_id: uuid.UUID
    amount: Decimal
    balance_after: Decimal
    note: str | None = None
    change_type: BalanceChangeType
    order_id: uuid.UUID | None = None
    created_by_id: uuid.UUID | None = None
