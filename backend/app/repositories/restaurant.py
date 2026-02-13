import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.restaurant import Dish, Restaurant
from app.repositories.base import BaseRepository


class RestaurantRepository(BaseRepository[Restaurant]):
    def __init__(self, session: AsyncSession):
        super().__init__(Restaurant, session)

    async def get_by_group(self, group_id: uuid.UUID) -> list[Restaurant]:
        query = select(Restaurant).where(Restaurant.group_id == group_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_name_and_group(self, name: str, group_id: uuid.UUID) -> Restaurant | None:
        query = select(Restaurant).where(
            Restaurant.name == name,
            Restaurant.group_id == group_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_dishes(self, restaurant_id: uuid.UUID) -> Restaurant | None:
        query = select(Restaurant).where(Restaurant.id == restaurant_id).options(joinedload(Restaurant.dishes))
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()


class DishRepository(BaseRepository[Dish]):
    def __init__(self, session: AsyncSession):
        super().__init__(Dish, session)

    async def get_by_restaurant(self, restaurant_id: uuid.UUID) -> list[Dish]:
        query = select(Dish).where(Dish.restaurant_id == restaurant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_name_and_restaurant(self, name: str, restaurant_id: uuid.UUID) -> Dish | None:
        query = select(Dish).where(
            Dish.name == name,
            Dish.restaurant_id == restaurant_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
