import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderDetailResponse
from app.workflows.order.get_detail import GetOrderDetailInput, GetOrderDetailWorkflow


class GetActiveOrderInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class GetActiveOrderOutput(BaseModel):
    order: OrderDetailResponse | None


class GetActiveOrderWorkflow:
    def __init__(
        self,
        order_repository: OrderRepository,
        group_member_repository: GroupMemberRepository,
        get_detail_workflow: GetOrderDetailWorkflow,
    ):
        self.order_repository = order_repository
        self.group_member_repository = group_member_repository
        self.get_detail_workflow = get_detail_workflow

    async def execute(self, input_data: GetActiveOrderInput) -> GetActiveOrderOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        order = await self.order_repository.get_active_for_group(input_data.group_id)
        if order is None:
            return GetActiveOrderOutput(order=None)

        result = await self.get_detail_workflow.execute(GetOrderDetailInput(order_id=order.id))
        return GetActiveOrderOutput(order=result.order)
