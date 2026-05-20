from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset import PasswordResetToken
from app.repositories.base import BaseRepository


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(PasswordResetToken, session)

    async def get_active_by_token(self, token: str) -> PasswordResetToken | None:
        query = select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used.is_(False),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
