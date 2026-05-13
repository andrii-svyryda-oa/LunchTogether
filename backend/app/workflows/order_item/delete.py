import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderItemRepository, OrderRepository


class DeleteOrderItemInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    order_id: uuid.UUID
    item_id: uuid.UUID
    current_user: User


class DeleteOrderItemOutput(BaseModel):
    deleted: bool


class DeleteOrderItemWorkflow:
    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: DeleteOrderItemInput) -> DeleteOrderItemOutput:
        user = input_data.current_user

        order = await self.order_repository.get_by_id(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        membership = None
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        is_initiator = order.initiator_id == user.id
        is_editor = membership and membership.get_permission(PermissionType.ORDERS) == OrdersScope.EDITOR

        if order.status == OrderStatus.INITIATED:
            pass
        elif order.status == OrderStatus.CONFIRMED:
            if not is_initiator and not is_editor and not user.is_admin:
                raise ForbiddenError(
                    detail="Only the order initiator or an editor can remove items in Confirmed status"
                )
        else:
            raise ForbiddenError(detail="Can only remove items from orders in Initiated or Confirmed status")

        item = await self.order_item_repository.get_by_id(input_data.item_id)
        if item is None or item.order_id != input_data.order_id:
            raise NotFoundError(detail="Order item not found")

        is_own_item = item.user_id == user.id
        if order.status == OrderStatus.INITIATED and not user.is_admin and not is_editor and not is_own_item:
            raise ForbiddenError(detail="You can only remove your own items")

        deleted = await self.order_item_repository.delete(input_data.item_id)
        return DeleteOrderItemOutput(deleted=deleted)
