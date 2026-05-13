import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import BalancesScope, PermissionType
from app.models.user import User
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.schemas.balance import BalanceHistoryResponse


class GetBalanceHistoryInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    user_id: uuid.UUID
    current_user: User


class GetBalanceHistoryOutput(BaseModel):
    history: list[BalanceHistoryResponse]


class GetBalanceHistoryWorkflow:
    def __init__(
        self,
        balance_repository: BalanceRepository,
        balance_history_repository: BalanceHistoryRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.balance_repository = balance_repository
        self.balance_history_repository = balance_history_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: GetBalanceHistoryInput) -> GetBalanceHistoryOutput:
        user = input_data.current_user
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            balances_level = membership.get_permission(PermissionType.BALANCES)
            if balances_level == BalancesScope.NONE or balances_level is None:
                raise ForbiddenError(detail="You do not have permission to view balances")

        balance = await self.balance_repository.get_by_user_and_group(input_data.user_id, input_data.group_id)
        if balance is None:
            raise NotFoundError(detail="Balance not found")

        history = await self.balance_history_repository.get_history_for_balance(balance.id)
        return GetBalanceHistoryOutput(
            history=[
                BalanceHistoryResponse(
                    **{k: getattr(h, k) for k in BalanceHistoryResponse.model_fields if hasattr(h, k)},
                    created_by_name=h.created_by.full_name if h.created_by else None,
                )
                for h in history
            ]
        )
