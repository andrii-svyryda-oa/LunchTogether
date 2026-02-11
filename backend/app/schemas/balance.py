import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.base import BaseSchema

# --- Balance ---


class BalanceResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    group_id: uuid.UUID
    amount: Decimal
    created_at: datetime
    updated_at: datetime
    user_full_name: str | None = None


# --- Balance Adjustment ---


class BalanceAdjustment(BaseSchema):
    user_id: uuid.UUID
    amount: Decimal = Field(decimal_places=2)
    note: str | None = Field(default=None, max_length=500)


# --- Balance History ---


class BalanceHistoryResponse(BaseSchema):
    id: uuid.UUID
    balance_id: uuid.UUID
    amount: Decimal
    balance_after: Decimal
    note: str | None
    change_type: str
    order_id: uuid.UUID | None
    created_by_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    created_by_name: str | None = None
