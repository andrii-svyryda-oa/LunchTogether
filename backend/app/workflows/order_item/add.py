import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderItemRepository, OrderRepository
from app.repositories.user import UserRepository
from app.schemas.internal import OrderItemInternalCreate
from app.schemas.order import OrderItemCreate, OrderItemResponse


class AddOrderItemInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    order_id: uuid.UUID
    data: OrderItemCreate
    current_user: User


class AddOrderItemOutput(BaseModel):
    item: OrderItemResponse


class AddOrderItemWorkflow:
    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        group_member_repository: GroupMemberRepository,
        user_repository: UserRepository,
    ):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.group_member_repository = group_member_repository
        self.user_repository = user_repository

    async def execute(self, input_data: AddOrderItemInput) -> AddOrderItemOutput:
        user = input_data.current_user

        membership = None
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        order = await self.order_repository.get_by_id(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        is_initiator = order.initiator_id == user.id
        is_editor = membership and membership.get_permission(PermissionType.ORDERS) == OrdersScope.EDITOR

        if order.status == OrderStatus.INITIATED:
            pass
        elif order.status == OrderStatus.CONFIRMED:
            if not is_initiator and not is_editor and not user.is_admin:
                raise ForbiddenError(
                    detail="Only the order initiator or an editor can modify items in Confirmed status"
                )
        else:
            raise ForbiddenError(detail="Can only add items to orders in Initiated or Confirmed status")

        target_user_id = user.id
        target_user_name = user.full_name
        if input_data.data.user_id is not None and input_data.data.user_id != user.id:
            if not is_initiator and not is_editor and not user.is_admin:
                raise ForbiddenError(detail="Only the order initiator or an editor can add items for other members")
            target_user_id = input_data.data.user_id
            target_user = await self.user_repository.get_by_id(input_data.data.user_id)
            target_user_name = target_user.full_name if target_user else None

        item = await self.order_item_repository.create(
            OrderItemInternalCreate(
                order_id=input_data.order_id,
                user_id=target_user_id,
                name=input_data.data.name,
                detail=input_data.data.detail,
                price=input_data.data.price,
                dish_id=input_data.data.dish_id,
                quantity=input_data.data.quantity,
            )
        )
        return AddOrderItemOutput(
            item=OrderItemResponse(
                **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
                user_full_name=target_user_name,
            )
        )
