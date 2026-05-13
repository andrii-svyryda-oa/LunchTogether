import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderItemRepository
from app.schemas.order import OrderItemResponse


class ListOrderItemsInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    order_id: uuid.UUID
    current_user: User


class ListOrderItemsOutput(BaseModel):
    items: list[OrderItemResponse]


class ListOrderItemsWorkflow:
    def __init__(
        self,
        order_item_repository: OrderItemRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.order_item_repository = order_item_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: ListOrderItemsInput) -> ListOrderItemsOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        items = await self.order_item_repository.get_items_for_order(input_data.order_id)
        return ListOrderItemsOutput(
            items=[
                OrderItemResponse(
                    **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
                    user_full_name=item.user.full_name if item.user else None,
                )
                for item in items
            ]
        )
