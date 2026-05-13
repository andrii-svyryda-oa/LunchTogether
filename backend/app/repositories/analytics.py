import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.balance import Balance
from app.models.enums import OrderStatus
from app.models.group import GroupMember
from app.models.order import Order, OrderItem


class GroupAnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_orders(self, group_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Order).where(Order.group_id == group_id)
        return (await self.session.execute(query)).scalar_one()

    async def count_completed_orders(self, group_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Order).where(
            Order.group_id == group_id, Order.status == OrderStatus.FINISHED
        )
        return (await self.session.execute(query)).scalar_one()

    async def count_cancelled_orders(self, group_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Order).where(
            Order.group_id == group_id, Order.status == OrderStatus.CANCELLED
        )
        return (await self.session.execute(query)).scalar_one()

    async def count_active_orders(self, group_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(Order)
            .where(
                Order.group_id == group_id,
                Order.status.notin_([OrderStatus.FINISHED, OrderStatus.CANCELLED]),
            )
        )
        return (await self.session.execute(query)).scalar_one()

    async def count_members(self, group_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)
        return (await self.session.execute(query)).scalar_one()

    async def get_total_spent(self, group_id: uuid.UUID) -> Decimal:
        items_query = (
            select(func.coalesce(func.sum(OrderItem.price), 0))
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.group_id == group_id, Order.status == OrderStatus.FINISHED)
        )
        items_spent = (await self.session.execute(items_query)).scalar_one()

        delivery_query = select(func.coalesce(func.sum(Order.delivery_fee_total), 0)).where(
            Order.group_id == group_id, Order.status == OrderStatus.FINISHED
        )
        delivery_spent = (await self.session.execute(delivery_query)).scalar_one()

        return Decimal(str(items_spent)) + Decimal(str(delivery_spent))

    async def get_most_popular_restaurant(self, group_id: uuid.UUID) -> str | None:
        query = (
            select(Order.restaurant_name, func.count().label("cnt"))
            .where(Order.group_id == group_id, Order.restaurant_name.isnot(None))
            .group_by(Order.restaurant_name)
            .order_by(func.count().desc())
            .limit(1)
        )
        result = (await self.session.execute(query)).first()
        return result[0] if result else None


class UserAnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_groups(self, user_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(GroupMember).where(GroupMember.user_id == user_id)
        return (await self.session.execute(query)).scalar_one()

    async def count_orders_participated(self, user_id: uuid.UUID) -> int:
        query = select(func.count(func.distinct(OrderItem.order_id))).where(OrderItem.user_id == user_id)
        return (await self.session.execute(query)).scalar_one()

    async def get_total_spent(self, user_id: uuid.UUID) -> Decimal:
        items_query = (
            select(func.coalesce(func.sum(OrderItem.price), 0))
            .join(Order, OrderItem.order_id == Order.id)
            .where(OrderItem.user_id == user_id, Order.status == OrderStatus.FINISHED)
        )
        items_spent = (await self.session.execute(items_query)).scalar_one()

        user_orders_subquery = (
            select(func.distinct(OrderItem.order_id)).where(OrderItem.user_id == user_id).scalar_subquery()
        )
        delivery_query = select(func.coalesce(func.sum(Order.delivery_fee_per_person), 0)).where(
            Order.id.in_(user_orders_subquery), Order.status == OrderStatus.FINISHED
        )
        delivery_spent = (await self.session.execute(delivery_query)).scalar_one()

        return Decimal(str(items_spent)) + Decimal(str(delivery_spent))

    async def get_favorite_restaurant(self, user_id: uuid.UUID) -> str | None:
        query = (
            select(Order.restaurant_name, func.count().label("cnt"))
            .join(OrderItem, Order.id == OrderItem.order_id)
            .where(OrderItem.user_id == user_id, Order.restaurant_name.isnot(None))
            .group_by(Order.restaurant_name)
            .order_by(func.count().desc())
            .limit(1)
        )
        result = (await self.session.execute(query)).first()
        return result[0] if result else None

    async def get_total_balance(self, user_id: uuid.UUID) -> Decimal:
        query = select(func.coalesce(func.sum(Balance.amount), 0)).where(Balance.user_id == user_id)
        result = (await self.session.execute(query)).scalar_one()
        return Decimal(str(result))
