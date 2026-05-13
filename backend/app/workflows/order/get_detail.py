import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.repositories.order import OrderRepository
from app.schemas.order import OrderDetailResponse, OrderItemResponse, OrderResponse


class GetOrderDetailInput(BaseModel):
    order_id: uuid.UUID


class GetOrderDetailOutput(BaseModel):
    order: OrderDetailResponse


class GetOrderDetailWorkflow:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, input_data: GetOrderDetailInput) -> GetOrderDetailOutput:
        order = await self.order_repository.get_with_items(input_data.order_id)
        if order is None:
            raise NotFoundError(detail="Order not found")

        items = [
            OrderItemResponse(
                **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
                user_full_name=item.user.full_name if item.user else None,
            )
            for item in order.items
        ]

        participants = {item.user_id for item in order.items}
        total_amount = sum(item.price * (item.quantity or 1) for item in order.items)

        return GetOrderDetailOutput(
            order=OrderDetailResponse(
                **{k: getattr(order, k) for k in OrderResponse.model_fields if hasattr(order, k)},
                items=items,
                initiator_name=order.initiator.full_name if order.initiator else None,
                participant_count=len(participants),
                total_amount=Decimal(str(total_amount)),
            )
        )
