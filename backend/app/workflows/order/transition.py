import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.enums import BalanceChangeType, OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderItemRepository, OrderRepository
from app.repositories.restaurant import DishRepository
from app.schemas.internal import (
    BalanceAmountUpdate,
    BalanceHistoryInternalCreate,
    BalanceInternalCreate,
    DishInternalCreate,
    OrderStatusInternalUpdate,
)
from app.schemas.order import OrderResponse

VALID_TRANSITIONS = {
    OrderStatus.INITIATED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.ORDERED, OrderStatus.CANCELLED],
    OrderStatus.ORDERED: [OrderStatus.FINISHED, OrderStatus.CANCELLED],
}


class TransitionOrderInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    order_id: uuid.UUID
    new_status: str
    current_user: User


class TransitionOrderOutput(BaseModel):
    order: OrderResponse


class TransitionOrderWorkflow:
    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        group_member_repository: GroupMemberRepository,
        balance_repository: BalanceRepository,
        balance_history_repository: BalanceHistoryRepository,
        dish_repository: DishRepository,
    ):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.group_member_repository = group_member_repository
        self.balance_repository = balance_repository
        self.balance_history_repository = balance_history_repository
        self.dish_repository = dish_repository

    async def execute(self, input_data: TransitionOrderInput) -> TransitionOrderOutput:
        user = input_data.current_user

        order = await self.order_repository.get_by_id(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        membership = await self.group_member_repository.get_membership(user.id, order.group_id)
        is_initiator = order.initiator_id == user.id
        is_editor = membership and membership.get_permission(PermissionType.ORDERS) == OrdersScope.EDITOR

        if not is_initiator and not is_editor and not user.is_admin:
            raise ForbiddenError(detail="Only the order initiator or an editor can change order status")

        current_status = OrderStatus(order.status)
        new_status = OrderStatus(input_data.new_status)

        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValidationError(detail=f"Cannot transition from {current_status.value} to {new_status.value}")

        if new_status == OrderStatus.FINISHED:
            await self._handle_finish(order)

        updated = await self.order_repository.update(order.id, OrderStatusInternalUpdate(status=new_status.value))

        return TransitionOrderOutput(order=OrderResponse.model_validate(updated))

    async def _handle_finish(self, order) -> None:
        items = await self.order_item_repository.get_items_for_order(order.id)
        if not items:
            return

        user_totals: dict[uuid.UUID, Decimal] = {}
        for item in items:
            user_totals.setdefault(item.user_id, Decimal("0.00"))
            user_totals[item.user_id] += item.price * (item.quantity or 1)

        if order.delivery_fee_per_person:
            for uid in user_totals:
                user_totals[uid] += order.delivery_fee_per_person

        for uid, total in user_totals.items():
            balance = await self.balance_repository.get_by_user_and_group(uid, order.group_id)
            if balance is None:
                balance = await self.balance_repository.create(
                    BalanceInternalCreate(user_id=uid, group_id=order.group_id)
                )
            new_amount = balance.amount - total
            await self.balance_repository.update(balance.id, BalanceAmountUpdate(amount=new_amount))

            await self.balance_history_repository.create(
                BalanceHistoryInternalCreate(
                    balance_id=balance.id,
                    amount=-total,
                    balance_after=new_amount,
                    note=f"Order #{str(order.id)[:8]}",
                    change_type=BalanceChangeType.ORDER,
                    order_id=order.id,
                )
            )

        if order.restaurant_id:
            for item in items:
                existing_dish = await self.dish_repository.get_by_name_and_restaurant(item.name, order.restaurant_id)
                if existing_dish:
                    if existing_dish.price != item.price:
                        from app.schemas.restaurant import DishUpdate

                        await self.dish_repository.update(existing_dish.id, DishUpdate(price=item.price))
                else:
                    await self.dish_repository.create(
                        DishInternalCreate(
                            name=item.name,
                            detail=item.detail,
                            price=item.price,
                            restaurant_id=order.restaurant_id,
                        )
                    )
