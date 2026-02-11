import uuid

from fastapi import APIRouter, Depends

from app.core.exceptions import ForbiddenError, NotFoundError
from app.dependencies import (
    get_current_user,
    get_dish_repository,
    get_group_member_repository,
    get_restaurant_repository,
)
from app.models.enums import RestaurantsScope
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import DishRepository, RestaurantRepository
from app.schemas.base import MessageResponse
from app.schemas.restaurant import (
    DishCreate,
    DishResponse,
    DishUpdate,
    RestaurantCreate,
    RestaurantDetailResponse,
    RestaurantResponse,
    RestaurantUpdate,
)

router = APIRouter(prefix="/groups/{group_id}/restaurants", tags=["restaurants"])


async def _check_restaurant_permission(
    user: User,
    group_id: uuid.UUID,
    group_member_repository: GroupMemberRepository,
    require_editor: bool = False,
) -> None:
    if user.is_admin:
        return
    membership = await group_member_repository.get_membership(user.id, group_id)
    if membership is None:
        raise ForbiddenError(detail="You are not a member of this group")
    if require_editor and membership.restaurants_scope != RestaurantsScope.EDITOR:
        raise ForbiddenError(detail="You do not have permission to manage restaurants")


# --- Restaurant CRUD ---


@router.get("", response_model=list[RestaurantResponse])
async def list_restaurants(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> list[RestaurantResponse]:
    await _check_restaurant_permission(current_user, group_id, group_member_repository)
    restaurants = await restaurant_repository.get_by_group(group_id)
    return [RestaurantResponse.model_validate(r) for r in restaurants]


@router.post("", response_model=RestaurantResponse, status_code=201)
async def create_restaurant(
    group_id: uuid.UUID,
    data: RestaurantCreate,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> RestaurantResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository, require_editor=True)
    restaurant = await restaurant_repository.create(
        {
            "name": data.name,
            "description": data.description,
            "group_id": group_id,
        }
    )
    return RestaurantResponse.model_validate(restaurant)


@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
async def get_restaurant(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> RestaurantDetailResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository)
    restaurant = await restaurant_repository.get_with_dishes(restaurant_id)
    if restaurant is None or restaurant.group_id != group_id:
        raise NotFoundError(detail="Restaurant not found")
    dishes = [DishResponse.model_validate(d) for d in restaurant.dishes]
    return RestaurantDetailResponse(
        **{k: getattr(restaurant, k) for k in RestaurantResponse.model_fields if hasattr(restaurant, k)},
        dishes=dishes,
    )


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    data: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> RestaurantResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository, require_editor=True)
    restaurant = await restaurant_repository.get_by_id(restaurant_id)
    if restaurant is None or restaurant.group_id != group_id:
        raise NotFoundError(detail="Restaurant not found")
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return RestaurantResponse.model_validate(restaurant)
    updated = await restaurant_repository.update(restaurant_id, update_data)
    return RestaurantResponse.model_validate(updated)


@router.delete("/{restaurant_id}", response_model=MessageResponse)
async def delete_restaurant(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> MessageResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository, require_editor=True)
    restaurant = await restaurant_repository.get_by_id(restaurant_id)
    if restaurant is None or restaurant.group_id != group_id:
        raise NotFoundError(detail="Restaurant not found")
    await restaurant_repository.delete(restaurant_id)
    return MessageResponse(message="Restaurant deleted successfully")


# --- Dish CRUD ---


@router.get("/{restaurant_id}/dishes", response_model=list[DishResponse])
async def list_dishes(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> list[DishResponse]:
    await _check_restaurant_permission(current_user, group_id, group_member_repository)
    dishes = await dish_repository.get_by_restaurant(restaurant_id)
    return [DishResponse.model_validate(d) for d in dishes]


@router.post("/{restaurant_id}/dishes", response_model=DishResponse, status_code=201)
async def create_dish(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    data: DishCreate,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> DishResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository, require_editor=True)
    # Verify restaurant belongs to group
    restaurant = await restaurant_repository.get_by_id(restaurant_id)
    if restaurant is None or restaurant.group_id != group_id:
        raise NotFoundError(detail="Restaurant not found")
    dish = await dish_repository.create(
        {
            "name": data.name,
            "detail": data.detail,
            "price": data.price,
            "restaurant_id": restaurant_id,
        }
    )
    return DishResponse.model_validate(dish)


@router.patch("/{restaurant_id}/dishes/{dish_id}", response_model=DishResponse)
async def update_dish(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    dish_id: uuid.UUID,
    data: DishUpdate,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> DishResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository, require_editor=True)
    dish = await dish_repository.get_by_id(dish_id)
    if dish is None or dish.restaurant_id != restaurant_id:
        raise NotFoundError(detail="Dish not found")
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return DishResponse.model_validate(dish)
    updated = await dish_repository.update(dish_id, update_data)
    return DishResponse.model_validate(updated)


@router.delete("/{restaurant_id}/dishes/{dish_id}", response_model=MessageResponse)
async def delete_dish(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    dish_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> MessageResponse:
    await _check_restaurant_permission(current_user, group_id, group_member_repository, require_editor=True)
    dish = await dish_repository.get_by_id(dish_id)
    if dish is None or dish.restaurant_id != restaurant_id:
        raise NotFoundError(detail="Dish not found")
    await dish_repository.delete(dish_id)
    return MessageResponse(message="Dish deleted successfully")
