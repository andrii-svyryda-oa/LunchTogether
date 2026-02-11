import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.balance import Balance, BalanceHistory
from app.repositories.base import BaseRepository


class BalanceRepository(BaseRepository[Balance]):
    def __init__(self, session: AsyncSession):
        super().__init__(Balance, session)

    async def get_by_user_and_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Balance | None:
        query = select(Balance).where(
            Balance.user_id == user_id,
            Balance.group_id == group_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Balance:
        balance = await self.get_by_user_and_group(user_id, group_id)
        if balance is None:
            balance = await self.create(
                {
                    "user_id": user_id,
                    "group_id": group_id,
                }
            )
        return balance

    async def get_balances_for_group(self, group_id: uuid.UUID) -> list[Balance]:
        query = select(Balance).where(Balance.group_id == group_id).options(joinedload(Balance.user))
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_balances_for_user(self, user_id: uuid.UUID) -> list[Balance]:
        query = select(Balance).where(Balance.user_id == user_id).options(joinedload(Balance.group))
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())


class BalanceHistoryRepository(BaseRepository[BalanceHistory]):
    def __init__(self, session: AsyncSession):
        super().__init__(BalanceHistory, session)

    async def get_history_for_balance(self, balance_id: uuid.UUID) -> list[BalanceHistory]:
        query = (
            select(BalanceHistory)
            .where(BalanceHistory.balance_id == balance_id)
            .order_by(BalanceHistory.created_at.desc())
            .options(joinedload(BalanceHistory.created_by))
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())
