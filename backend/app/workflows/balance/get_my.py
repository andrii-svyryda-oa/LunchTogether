import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.balance import BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.schemas.balance import BalanceResponse
from app.schemas.internal import BalanceInternalCreate


class GetMyBalanceInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class GetMyBalanceOutput(BaseModel):
    balance: BalanceResponse


class GetMyBalanceWorkflow:
    def __init__(
        self,
        balance_repository: BalanceRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.balance_repository = balance_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: GetMyBalanceInput) -> GetMyBalanceOutput:
        user = input_data.current_user
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        balance = await self.balance_repository.get_by_user_and_group(user.id, input_data.group_id)
        if balance is None:
            balance = await self.balance_repository.create(
                BalanceInternalCreate(user_id=user.id, group_id=input_data.group_id)
            )

        return GetMyBalanceOutput(balance=BalanceResponse.model_validate(balance))
