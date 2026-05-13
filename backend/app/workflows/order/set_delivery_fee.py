import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.enums import OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderItemRepository, OrderRepository
from app.schemas.internal import OrderDeliveryFeeInternalUpdate
from app.schemas.order import OrderDeliveryFeeUpdate, OrderResponse


class SetDeliveryFeeInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    order_id: uuid.UUID
    data: OrderDeliveryFeeUpdate
    current_user: User


class SetDeliveryFeeOutput(BaseModel):
    order: OrderResponse


class SetDeliveryFeeWorkflow:
    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: SetDeliveryFeeInput) -> SetDeliveryFeeOutput:
        user = input_data.current_user

        order = await self.order_repository.get_by_id(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        if order.status in (OrderStatus.FINISHED, OrderStatus.CANCELLED):
            raise ValidationError(detail="Delivery fees cannot be changed on finished or cancelled orders")

        membership = await self.group_member_repository.get_membership(user.id, order.group_id)
        is_initiator = order.initiator_id == user.id
        is_editor = membership and membership.get_permission(PermissionType.ORDERS) == OrdersScope.EDITOR

        if not is_initiator and not is_editor and not user.is_admin:
            raise ForbiddenError(detail="Only the order initiator or an editor can set delivery fees")

        updated = order
        if input_data.data.delivery_fee_total is not None:
            participants = await self.order_item_repository.get_unique_participants(order.id)
            if len(participants) > 0:
                per_person = input_data.data.delivery_fee_total / Decimal(str(len(participants)))
                updated = await self.order_repository.update(
                    order.id,
                    OrderDeliveryFeeInternalUpdate(
                        delivery_fee_total=input_data.data.delivery_fee_total,
                        delivery_fee_per_person=per_person.quantize(Decimal("0.01")),
                    ),
                )
        elif input_data.data.delivery_fee_per_person is not None:
            participants = await self.order_item_repository.get_unique_participants(order.id)
            total = input_data.data.delivery_fee_per_person * Decimal(str(len(participants)))
            updated = await self.order_repository.update(
                order.id,
                OrderDeliveryFeeInternalUpdate(
                    delivery_fee_per_person=input_data.data.delivery_fee_per_person,
                    delivery_fee_total=total.quantize(Decimal("0.01")),
                ),
            )

        return SetDeliveryFeeOutput(order=OrderResponse.model_validate(updated))
