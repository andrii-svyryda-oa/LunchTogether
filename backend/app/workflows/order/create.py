import uuid

from pydantic import BaseModel

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository, GroupRepository
from app.repositories.order import OrderRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.order import OrderCreate, OrderResponse


class CreateOrderInput(BaseModel):
    group_id: uuid.UUID
    data: OrderCreate
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class CreateOrderOutput(BaseModel):
    order: OrderResponse


class CreateOrderWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        order_repository: OrderRepository,
        restaurant_repository: RestaurantRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.order_repository = order_repository
        self.restaurant_repository = restaurant_repository

    async def execute(self, input_data: CreateOrderInput) -> CreateOrderOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        # Verify group exists
        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        # Check permission
        membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
        if membership is None and not user.is_admin:
            raise ForbiddenError(detail="You are not a member of this group")

        orders_level = membership.get_permission(PermissionType.ORDERS) if membership else None
        if membership and orders_level not in (OrdersScope.EDITOR, OrdersScope.INITIATOR):
            raise ForbiddenError(detail="You do not have permission to create orders")

        # Check no active order exists
        active_order = await self.order_repository.get_active_for_group(input_data.group_id)
        if active_order is not None:
            raise ForbiddenError(detail="There is already an active order in this group")

        # Resolve restaurant name
        restaurant_name = input_data.data.restaurant_name
        if input_data.data.restaurant_id:
            restaurant = await self.restaurant_repository.get_by_id(input_data.data.restaurant_id)
            if restaurant:
                restaurant_name = restaurant.name

        order = await self.order_repository.create(
            {
                "group_id": input_data.group_id,
                "restaurant_id": input_data.data.restaurant_id,
                "restaurant_name": restaurant_name,
                "initiator_id": user.id,
                "status": OrderStatus.INITIATED,
            }
        )

        return CreateOrderOutput(order=OrderResponse.model_validate(order))
