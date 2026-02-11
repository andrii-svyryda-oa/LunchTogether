from decimal import Decimal

from app.schemas.base import BaseSchema


class GroupAnalytics(BaseSchema):
    total_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    active_orders: int = 0
    total_members: int = 0
    total_spent: Decimal = Decimal("0.00")
    average_order_value: Decimal = Decimal("0.00")
    most_popular_restaurant: str | None = None
    most_active_member: str | None = None


class UserAnalytics(BaseSchema):
    total_groups: int = 0
    total_orders_participated: int = 0
    total_spent: Decimal = Decimal("0.00")
    average_order_value: Decimal = Decimal("0.00")
    favorite_restaurant: str | None = None
    total_balance_across_groups: Decimal = Decimal("0.00")
