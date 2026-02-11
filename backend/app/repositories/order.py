import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.enums import OrderStatus
from app.models.order import FavoriteDish, Order, OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_group(self, group_id: uuid.UUID) -> list[Order]:
        query = select(Order).where(Order.group_id == group_id).order_by(Order.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_for_group(self, group_id: uuid.UUID) -> Order | None:
        """Get the current active (non-finished, non-cancelled) order for a group."""
        query = select(Order).where(
            Order.group_id == group_id,
            Order.status.notin_([OrderStatus.FINISHED, OrderStatus.CANCELLED]),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_items(self, order_id: uuid.UUID) -> Order | None:
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                joinedload(Order.items).joinedload(OrderItem.user),
                joinedload(Order.initiator),
            )
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def count_by_group(self, group_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Order).where(Order.group_id == group_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_by_status(self, group_id: uuid.UUID, status: str) -> int:
        query = (
            select(func.count())
            .select_from(Order)
            .where(
                Order.group_id == group_id,
                Order.status == status,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_orders_for_user(self, user_id: uuid.UUID) -> list[Order]:
        """Get all orders where a user has items."""
        query = (
            select(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .where(OrderItem.user_id == user_id)
            .distinct()
            .order_by(Order.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(OrderItem, session)

    async def get_items_for_order(self, order_id: uuid.UUID) -> list[OrderItem]:
        query = select(OrderItem).where(OrderItem.order_id == order_id).options(joinedload(OrderItem.user))
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_user_items_for_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> list[OrderItem]:
        query = select(OrderItem).where(
            OrderItem.order_id == order_id,
            OrderItem.user_id == user_id,
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_unique_participants(self, order_id: uuid.UUID) -> list[uuid.UUID]:
        query = select(OrderItem.user_id).where(OrderItem.order_id == order_id).distinct()
        result = await self.session.execute(query)
        return list(result.scalars().all())


class FavoriteDishRepository(BaseRepository[FavoriteDish]):
    def __init__(self, session: AsyncSession):
        super().__init__(FavoriteDish, session)

    async def get_favorites_for_user(self, user_id: uuid.UUID, restaurant_id: uuid.UUID) -> list[FavoriteDish]:
        query = (
            select(FavoriteDish)
            .join(FavoriteDish.dish)
            .where(
                FavoriteDish.user_id == user_id,
                FavoriteDish.is_favorite.is_(True),
            )
            .filter_by(restaurant_id=restaurant_id)
            .options(joinedload(FavoriteDish.dish))
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_user_and_dish(self, user_id: uuid.UUID, dish_id: uuid.UUID) -> FavoriteDish | None:
        query = select(FavoriteDish).where(
            FavoriteDish.user_id == user_id,
            FavoriteDish.dish_id == dish_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
