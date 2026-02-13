import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.enums import BalanceChangeType, OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.repositories.order import OrderItemRepository, OrderRepository
from app.repositories.restaurant import DishRepository
from app.schemas.order import OrderDetailResponse, OrderItemResponse, OrderResponse, OrderSetDeliveryFee


class TransitionOrderInput(BaseModel):
    order_id: uuid.UUID
    new_status: str
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class TransitionOrderOutput(BaseModel):
    order: OrderResponse


class SetDeliveryFeeInput(BaseModel):
    order_id: uuid.UUID
    data: OrderSetDeliveryFee
    current_user: object

    class Config:
        arbitrary_types_allowed = True


# Valid transitions
VALID_TRANSITIONS = {
    OrderStatus.INITIATED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.ORDERED, OrderStatus.CANCELLED],
    OrderStatus.ORDERED: [OrderStatus.FINISHED, OrderStatus.CANCELLED],
}


class OrderLifecycleWorkflow:
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

    async def transition(self, input_data: TransitionOrderInput) -> TransitionOrderOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        order = await self.order_repository.get_by_id(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        # Check user is the initiator or has editor permission
        membership = await self.group_member_repository.get_membership(user.id, order.group_id)
        is_initiator = order.initiator_id == user.id
        is_editor = membership and membership.get_permission(PermissionType.ORDERS) == OrdersScope.EDITOR

        if not is_initiator and not is_editor and not user.is_admin:
            raise ForbiddenError(detail="Only the order initiator or an editor can change order status")

        # Validate transition
        current_status = OrderStatus(order.status)
        new_status = OrderStatus(input_data.new_status)

        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValidationError(detail=f"Cannot transition from {current_status.value} to {new_status.value}")

        # Handle finishing: update balances and restaurant dishes
        if new_status == OrderStatus.FINISHED:
            await self._handle_finish(order)

        updated = await self.order_repository.update(order.id, {"status": new_status.value})

        return TransitionOrderOutput(order=OrderResponse.model_validate(updated))

    async def set_delivery_fee(self, input_data: SetDeliveryFeeInput) -> TransitionOrderOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        order = await self.order_repository.get_by_id(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        if order.status in (OrderStatus.FINISHED, OrderStatus.CANCELLED):
            raise ValidationError(detail="Delivery fees cannot be changed on finished or cancelled orders")

        # Only initiator or editor
        membership = await self.group_member_repository.get_membership(user.id, order.group_id)
        is_initiator = order.initiator_id == user.id
        is_editor = membership and membership.get_permission(PermissionType.ORDERS) == OrdersScope.EDITOR

        if not is_initiator and not is_editor and not user.is_admin:
            raise ForbiddenError(detail="Only the order initiator or an editor can set delivery fees")

        update_data: dict = {}
        if input_data.data.delivery_fee_total is not None:
            # Calculate per-person from total
            participants = await self.order_item_repository.get_unique_participants(order.id)
            if len(participants) > 0:
                per_person = input_data.data.delivery_fee_total / Decimal(str(len(participants)))
                update_data["delivery_fee_total"] = input_data.data.delivery_fee_total
                update_data["delivery_fee_per_person"] = per_person.quantize(Decimal("0.01"))
        elif input_data.data.delivery_fee_per_person is not None:
            participants = await self.order_item_repository.get_unique_participants(order.id)
            total = input_data.data.delivery_fee_per_person * Decimal(str(len(participants)))
            update_data["delivery_fee_per_person"] = input_data.data.delivery_fee_per_person
            update_data["delivery_fee_total"] = total.quantize(Decimal("0.01"))

        if update_data:
            updated = await self.order_repository.update(order.id, update_data)
        else:
            updated = order

        return TransitionOrderOutput(order=OrderResponse.model_validate(updated))

    async def _handle_finish(self, order) -> None:
        """Handle order finishing: update balances and restaurant dishes."""
        items = await self.order_item_repository.get_items_for_order(order.id)
        if not items:
            return

        # Group items by user and calculate totals (price * quantity)
        user_totals: dict[uuid.UUID, Decimal] = {}
        for item in items:
            user_totals.setdefault(item.user_id, Decimal("0.00"))
            user_totals[item.user_id] += item.price * (item.quantity or 1)

        # Add delivery fee per person if set
        if order.delivery_fee_per_person:
            for uid in user_totals:
                user_totals[uid] += order.delivery_fee_per_person

        # Update balances for each participant
        for uid, total in user_totals.items():
            balance = await self.balance_repository.get_or_create(uid, order.group_id)
            new_amount = balance.amount - total
            await self.balance_repository.update(balance.id, {"amount": new_amount})

            await self.balance_history_repository.create(
                {
                    "balance_id": balance.id,
                    "amount": -total,
                    "balance_after": new_amount,
                    "note": f"Order #{str(order.id)[:8]}",
                    "change_type": BalanceChangeType.ORDER,
                    "order_id": order.id,
                }
            )

        # Update restaurant dishes if restaurant is linked
        if order.restaurant_id:
            for item in items:
                existing_dish = await self.dish_repository.get_by_name_and_restaurant(item.name, order.restaurant_id)
                if existing_dish:
                    # Update price if different
                    if existing_dish.price != item.price:
                        await self.dish_repository.update(existing_dish.id, {"price": item.price})
                else:
                    # Create new dish
                    await self.dish_repository.create(
                        {
                            "name": item.name,
                            "detail": item.detail,
                            "price": item.price,
                            "restaurant_id": order.restaurant_id,
                        }
                    )

    async def get_order_detail(self, order_id: uuid.UUID) -> OrderDetailResponse:
        order = await self.order_repository.get_with_items(order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        items = [
            OrderItemResponse(
                **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
                user_full_name=item.user.full_name if item.user else None,
            )
            for item in order.items
        ]

        participants = set(item.user_id for item in order.items)
        total_amount = sum(item.price * (item.quantity or 1) for item in order.items)

        return OrderDetailResponse(
            **{k: getattr(order, k) for k in OrderResponse.model_fields if hasattr(order, k)},
            items=items,
            initiator_name=order.initiator.full_name if order.initiator else None,
            participant_count=len(participants),
            total_amount=total_amount,
        )
