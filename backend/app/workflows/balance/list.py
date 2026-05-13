import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.enums import BalancesScope, PermissionType
from app.models.user import User
from app.repositories.balance import BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.schemas.balance import BalanceResponse


class ListBalancesInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class ListBalancesOutput(BaseModel):
    balances: list[BalanceResponse]


class ListBalancesWorkflow:
    def __init__(
        self,
        balance_repository: BalanceRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.balance_repository = balance_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: ListBalancesInput) -> ListBalancesOutput:
        user = input_data.current_user
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            balances_level = membership.get_permission(PermissionType.BALANCES)
            if balances_level == BalancesScope.NONE or balances_level is None:
                raise ForbiddenError(detail="You do not have permission to view balances")

        balances = await self.balance_repository.get_balances_for_group(input_data.group_id)
        return ListBalancesOutput(
            balances=[
                BalanceResponse(
                    **{k: getattr(b, k) for k in BalanceResponse.model_fields if hasattr(b, k)},
                    user_full_name=b.user.full_name if b.user else None,
                )
                for b in balances
            ]
        )
