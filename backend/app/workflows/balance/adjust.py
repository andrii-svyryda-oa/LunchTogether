import uuid

from pydantic import BaseModel

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import BalanceChangeType, BalancesScope
from app.models.user import User
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.schemas.balance import BalanceAdjustment, BalanceResponse


class AdjustBalanceInput(BaseModel):
    group_id: uuid.UUID
    data: BalanceAdjustment
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class AdjustBalanceOutput(BaseModel):
    balance: BalanceResponse


class AdjustBalanceWorkflow:
    def __init__(
        self,
        balance_repository: BalanceRepository,
        balance_history_repository: BalanceHistoryRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.balance_repository = balance_repository
        self.balance_history_repository = balance_history_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: AdjustBalanceInput) -> AdjustBalanceOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        # Check user has Balances Editor permission
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            if membership.balances_scope != BalancesScope.EDITOR:
                raise ForbiddenError(detail="You do not have permission to adjust balances")

        # Check target user is a member
        target_membership = await self.group_member_repository.get_membership(
            input_data.data.user_id, input_data.group_id
        )
        if target_membership is None:
            raise NotFoundError(detail="Target user is not a member of this group")

        # Get or create balance
        balance = await self.balance_repository.get_or_create(input_data.data.user_id, input_data.group_id)

        # Apply adjustment
        new_amount = balance.amount + input_data.data.amount
        await self.balance_repository.update(balance.id, {"amount": new_amount})

        # Create history entry
        await self.balance_history_repository.create(
            {
                "balance_id": balance.id,
                "amount": input_data.data.amount,
                "balance_after": new_amount,
                "note": input_data.data.note,
                "change_type": BalanceChangeType.MANUAL,
                "created_by_id": user.id,
            }
        )

        # Refresh balance
        balance = await self.balance_repository.get_by_id(balance.id)

        return AdjustBalanceOutput(balance=BalanceResponse.model_validate(balance))
