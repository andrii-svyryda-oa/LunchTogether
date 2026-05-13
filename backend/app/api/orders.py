import uuid

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_add_order_item_workflow,
    get_create_order_workflow,
    get_current_user,
    get_delete_order_item_workflow,
    get_get_active_order_workflow,
    get_get_order_detail_workflow,
    get_list_favorites_workflow,
    get_list_order_items_workflow,
    get_list_orders_workflow,
    get_set_delivery_fee_workflow,
    get_toggle_favorite_workflow,
    get_transition_order_workflow,
    get_update_order_item_workflow,
)
from app.models.user import User
from app.schemas.base import MessageResponse
from app.schemas.order import (
    FavoriteDishResponse,
    OrderCreate,
    OrderDeliveryFeeUpdate,
    OrderDetailResponse,
    OrderItemCreate,
    OrderItemResponse,
    OrderItemUpdate,
    OrderResponse,
    OrderStatusUpdate,
)
from app.workflows.favorite.list import ListFavoritesInput, ListFavoritesWorkflow
from app.workflows.favorite.toggle import ToggleFavoriteInput, ToggleFavoriteWorkflow
from app.workflows.order.create import CreateOrderInput, CreateOrderWorkflow
from app.workflows.order.get_active import GetActiveOrderInput, GetActiveOrderWorkflow
from app.workflows.order.get_detail import GetOrderDetailInput, GetOrderDetailWorkflow
from app.workflows.order.list import ListOrdersInput, ListOrdersWorkflow
from app.workflows.order.set_delivery_fee import SetDeliveryFeeInput, SetDeliveryFeeWorkflow
from app.workflows.order.transition import TransitionOrderInput, TransitionOrderWorkflow
from app.workflows.order_item.add import AddOrderItemInput, AddOrderItemWorkflow
from app.workflows.order_item.delete import DeleteOrderItemInput, DeleteOrderItemWorkflow
from app.workflows.order_item.list import ListOrderItemsInput, ListOrderItemsWorkflow
from app.workflows.order_item.update import UpdateOrderItemInput, UpdateOrderItemWorkflow

router = APIRouter(prefix="/groups/{group_id}/orders", tags=["orders"])


# --- Order CRUD ---


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListOrdersWorkflow = Depends(get_list_orders_workflow),
) -> list[OrderResponse]:
    result = await workflow.execute(ListOrdersInput(group_id=group_id, current_user=current_user))
    return result.orders


@router.get("/active", response_model=OrderDetailResponse | None)
async def get_active_order(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: GetActiveOrderWorkflow = Depends(get_get_active_order_workflow),
) -> OrderDetailResponse | None:
    result = await workflow.execute(GetActiveOrderInput(group_id=group_id, current_user=current_user))
    return result.order


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    group_id: uuid.UUID,
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    workflow: CreateOrderWorkflow = Depends(get_create_order_workflow),
) -> OrderResponse:
    result = await workflow.execute(CreateOrderInput(group_id=group_id, data=data, current_user=current_user))
    return result.order


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: GetOrderDetailWorkflow = Depends(get_get_order_detail_workflow),
) -> OrderDetailResponse:
    result = await workflow.execute(GetOrderDetailInput(order_id=order_id))
    return result.order


@router.post("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    workflow: TransitionOrderWorkflow = Depends(get_transition_order_workflow),
) -> OrderResponse:
    result = await workflow.execute(
        TransitionOrderInput(order_id=order_id, new_status=data.status, current_user=current_user)
    )
    return result.order


@router.post("/{order_id}/delivery-fee", response_model=OrderResponse)
async def set_delivery_fee(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderDeliveryFeeUpdate,
    current_user: User = Depends(get_current_user),
    workflow: SetDeliveryFeeWorkflow = Depends(get_set_delivery_fee_workflow),
) -> OrderResponse:
    result = await workflow.execute(SetDeliveryFeeInput(order_id=order_id, data=data, current_user=current_user))
    return result.order


# --- Order Items ---


@router.get("/{order_id}/items", response_model=list[OrderItemResponse])
async def list_order_items(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListOrderItemsWorkflow = Depends(get_list_order_items_workflow),
) -> list[OrderItemResponse]:
    result = await workflow.execute(
        ListOrderItemsInput(group_id=group_id, order_id=order_id, current_user=current_user)
    )
    return result.items


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=201)
async def add_order_item(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderItemCreate,
    current_user: User = Depends(get_current_user),
    workflow: AddOrderItemWorkflow = Depends(get_add_order_item_workflow),
) -> OrderItemResponse:
    result = await workflow.execute(
        AddOrderItemInput(group_id=group_id, order_id=order_id, data=data, current_user=current_user)
    )
    return result.item


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    data: OrderItemUpdate,
    current_user: User = Depends(get_current_user),
    workflow: UpdateOrderItemWorkflow = Depends(get_update_order_item_workflow),
) -> OrderItemResponse:
    result = await workflow.execute(
        UpdateOrderItemInput(
            group_id=group_id, order_id=order_id, item_id=item_id, data=data, current_user=current_user
        )
    )
    return result.item


@router.delete("/{order_id}/items/{item_id}", response_model=MessageResponse)
async def delete_order_item(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: DeleteOrderItemWorkflow = Depends(get_delete_order_item_workflow),
) -> MessageResponse:
    await workflow.execute(
        DeleteOrderItemInput(group_id=group_id, order_id=order_id, item_id=item_id, current_user=current_user)
    )
    return MessageResponse(message="Order item removed successfully")


# --- Favorites ---


@router.get("/favorites/{restaurant_id}", response_model=list[FavoriteDishResponse])
async def get_favorites(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListFavoritesWorkflow = Depends(get_list_favorites_workflow),
) -> list[FavoriteDishResponse]:
    result = await workflow.execute(ListFavoritesInput(restaurant_id=restaurant_id, current_user=current_user))
    return result.favorites


@router.post("/favorites/{dish_id}", response_model=MessageResponse)
async def toggle_favorite(
    group_id: uuid.UUID,
    dish_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ToggleFavoriteWorkflow = Depends(get_toggle_favorite_workflow),
) -> MessageResponse:
    result = await workflow.execute(ToggleFavoriteInput(dish_id=dish_id, current_user=current_user))
    return MessageResponse(message=result.message)
