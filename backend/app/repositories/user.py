import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def update_password(self, user_id: uuid.UUID, hashed_password: str) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.hashed_password = hashed_password
        await self.session.flush()
        await self.session.refresh(user)
        return user
