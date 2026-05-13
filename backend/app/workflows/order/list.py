import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderResponse


class ListOrdersInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class ListOrdersOutput(BaseModel):
    orders: list[OrderResponse]


class ListOrdersWorkflow:
    def __init__(
        self,
        order_repository: OrderRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.order_repository = order_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: ListOrdersInput) -> ListOrdersOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        orders = await self.order_repository.get_by_group(input_data.group_id)
        return ListOrdersOutput(orders=[OrderResponse.model_validate(o) for o in orders])
