import uuid

from fastapi import APIRouter, Depends

from app.core.exceptions import ForbiddenError, NotFoundError
from app.dependencies import (
    get_create_order_workflow,
    get_current_user,
    get_favorite_dish_repository,
    get_group_member_repository,
    get_order_item_repository,
    get_order_lifecycle_workflow,
    get_order_repository,
)
from app.models.enums import OrdersScope, OrderStatus, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.order import FavoriteDishRepository, OrderItemRepository, OrderRepository
from app.schemas.base import MessageResponse
from app.schemas.order import (
    FavoriteDishResponse,
    OrderCreate,
    OrderDetailResponse,
    OrderItemCreate,
    OrderItemResponse,
    OrderItemUpdate,
    OrderResponse,
    OrderSetDeliveryFee,
    OrderUpdateStatus,
)
from app.workflows.order.create import CreateOrderInput, CreateOrderWorkflow
from app.workflows.order.lifecycle import (
    OrderLifecycleWorkflow,
    SetDeliveryFeeInput,
    TransitionOrderInput,
)

router = APIRouter(prefix="/groups/{group_id}/orders", tags=["orders"])


# --- Order CRUD ---


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> list[OrderResponse]:
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
    orders = await order_repository.get_by_group(group_id)
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/active", response_model=OrderDetailResponse | None)
async def get_active_order(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    lifecycle_workflow: OrderLifecycleWorkflow = Depends(get_order_lifecycle_workflow),
) -> OrderDetailResponse | None:
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
    order = await order_repository.get_active_for_group(group_id)
    if order is None:
        return None
    return await lifecycle_workflow.get_order_detail(order.id)


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
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    lifecycle_workflow: OrderLifecycleWorkflow = Depends(get_order_lifecycle_workflow),
) -> OrderDetailResponse:
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
    return await lifecycle_workflow.get_order_detail(order_id)


@router.post("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderUpdateStatus,
    current_user: User = Depends(get_current_user),
    lifecycle_workflow: OrderLifecycleWorkflow = Depends(get_order_lifecycle_workflow),
) -> OrderResponse:
    result = await lifecycle_workflow.transition(
        TransitionOrderInput(order_id=order_id, new_status=data.status, current_user=current_user)
    )
    return result.order


@router.post("/{order_id}/delivery-fee", response_model=OrderResponse)
async def set_delivery_fee(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderSetDeliveryFee,
    current_user: User = Depends(get_current_user),
    lifecycle_workflow: OrderLifecycleWorkflow = Depends(get_order_lifecycle_workflow),
) -> OrderResponse:
    result = await lifecycle_workflow.set_delivery_fee(
        SetDeliveryFeeInput(order_id=order_id, data=data, current_user=current_user)
    )
    return result.order


# --- Order Items ---


@router.get("/{order_id}/items", response_model=list[OrderItemResponse])
async def list_order_items(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
) -> list[OrderItemResponse]:
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
    items = await order_item_repository.get_items_for_order(order_id)
    return [
        OrderItemResponse(
            **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
            user_full_name=item.user.full_name if item.user else None,
        )
        for item in items
    ]


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=201)
async def add_order_item(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderItemCreate,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
) -> OrderItemResponse:
    # Check permission
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")

    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise NotFoundError(detail="Order not found")
    if order.status != OrderStatus.INITIATED:
        raise ForbiddenError(detail="Can only add items to orders in Initiated status")

    item = await order_item_repository.create(
        {
            "order_id": order_id,
            "user_id": current_user.id,
            "name": data.name,
            "detail": data.detail,
            "price": data.price,
            "dish_id": data.dish_id,
        }
    )
    return OrderItemResponse(
        **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
        user_full_name=current_user.full_name,
    )


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    data: OrderItemUpdate,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
) -> OrderItemResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise NotFoundError(detail="Order not found")
    if order.status != OrderStatus.INITIATED:
        raise ForbiddenError(detail="Can only edit items in orders in Initiated status")

    item = await order_item_repository.get_by_id(item_id)
    if item is None or item.order_id != order_id:
        raise NotFoundError(detail="Order item not found")

    # Permission check: Editor can edit any, others can only edit own
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
        if membership.get_permission(PermissionType.ORDERS) != OrdersScope.EDITOR and item.user_id != current_user.id:
            raise ForbiddenError(detail="You can only edit your own items")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return OrderItemResponse(
            **{k: getattr(item, k) for k in OrderItemResponse.model_fields if hasattr(item, k)},
        )
    updated = await order_item_repository.update(item_id, update_data)
    return OrderItemResponse(
        **{k: getattr(updated, k) for k in OrderItemResponse.model_fields if hasattr(updated, k)},
    )


@router.delete("/{order_id}/items/{item_id}", response_model=MessageResponse)
async def delete_order_item(
    group_id: uuid.UUID,
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
) -> MessageResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise NotFoundError(detail="Order not found")
    if order.status != OrderStatus.INITIATED:
        raise ForbiddenError(detail="Can only remove items from orders in Initiated status")

    item = await order_item_repository.get_by_id(item_id)
    if item is None or item.order_id != order_id:
        raise NotFoundError(detail="Order item not found")

    # Permission check
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
        if membership.get_permission(PermissionType.ORDERS) != OrdersScope.EDITOR and item.user_id != current_user.id:
            raise ForbiddenError(detail="You can only remove your own items")

    await order_item_repository.delete(item_id)
    return MessageResponse(message="Order item removed successfully")


# --- Favorites ---


@router.get("/favorites/{restaurant_id}", response_model=list[FavoriteDishResponse])
async def get_favorites(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    favorite_dish_repository: FavoriteDishRepository = Depends(get_favorite_dish_repository),
) -> list[FavoriteDishResponse]:
    favorites = await favorite_dish_repository.get_favorites_for_user(current_user.id, restaurant_id)
    return [
        FavoriteDishResponse(
            id=f.id,
            user_id=f.user_id,
            dish_id=f.dish_id,
            dish_name=f.dish.name if f.dish else None,
            dish_detail=f.dish.detail if f.dish else None,
            dish_price=f.dish.price if f.dish else None,
            restaurant_id=f.dish.restaurant_id if f.dish else None,
        )
        for f in favorites
    ]


@router.post("/favorites/{dish_id}", response_model=MessageResponse)
async def toggle_favorite(
    group_id: uuid.UUID,
    dish_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    favorite_dish_repository: FavoriteDishRepository = Depends(get_favorite_dish_repository),
) -> MessageResponse:
    existing = await favorite_dish_repository.get_by_user_and_dish(current_user.id, dish_id)
    if existing:
        new_status = not existing.is_favorite
        await favorite_dish_repository.update(existing.id, {"is_favorite": new_status})
        return MessageResponse(message=f"Dish {'favorited' if new_status else 'unfavorited'}")
    else:
        await favorite_dish_repository.create(
            {
                "user_id": current_user.id,
                "dish_id": dish_id,
                "is_favorite": True,
            }
        )
        return MessageResponse(message="Dish favorited")
