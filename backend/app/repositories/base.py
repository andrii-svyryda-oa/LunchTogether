import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel
from app.schemas.base import PaginatedResponse

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _base_query(self) -> Select:
        return select(self.model)

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelType | None:
        query = self._base_query().where(self.model.id == entity_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get(self, **filters: Any) -> ModelType | None:
        query = self._base_query()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        page: int = 1,
        page_size: int = 20,
        **filters: Any,
    ) -> PaginatedResponse:
        query = self._base_query()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create(self, data: dict[str, Any]) -> ModelType:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, entity_id: uuid.UUID, data: dict[str, Any]) -> ModelType | None:
        instance = await self.get_by_id(entity_id)
        if instance is None:
            return None

        for key, value in data.items():
            if value is not None:
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, entity_id: uuid.UUID) -> bool:
        instance = await self.get_by_id(entity_id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True
