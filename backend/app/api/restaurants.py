import uuid

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_create_dish_workflow,
    get_create_restaurant_workflow,
    get_current_user,
    get_delete_dish_workflow,
    get_delete_restaurant_workflow,
    get_get_restaurant_workflow,
    get_list_dishes_workflow,
    get_list_restaurants_workflow,
    get_update_dish_workflow,
    get_update_restaurant_workflow,
)
from app.models.user import User
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
from app.workflows.dish.create import CreateDishInput, CreateDishWorkflow
from app.workflows.dish.delete import DeleteDishInput, DeleteDishWorkflow
from app.workflows.dish.list import ListDishesInput, ListDishesWorkflow
from app.workflows.dish.update import UpdateDishInput, UpdateDishWorkflow
from app.workflows.restaurant.create import CreateRestaurantInput, CreateRestaurantWorkflow
from app.workflows.restaurant.delete import DeleteRestaurantInput, DeleteRestaurantWorkflow
from app.workflows.restaurant.get import GetRestaurantInput, GetRestaurantWorkflow
from app.workflows.restaurant.list import ListRestaurantsInput, ListRestaurantsWorkflow
from app.workflows.restaurant.update import UpdateRestaurantInput, UpdateRestaurantWorkflow

router = APIRouter(prefix="/groups/{group_id}/restaurants", tags=["restaurants"])


# --- Restaurant CRUD ---


@router.get("", response_model=list[RestaurantResponse])
async def list_restaurants(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListRestaurantsWorkflow = Depends(get_list_restaurants_workflow),
) -> list[RestaurantResponse]:
    result = await workflow.execute(ListRestaurantsInput(group_id=group_id, current_user=current_user))
    return result.restaurants


@router.post("", response_model=RestaurantResponse, status_code=201)
async def create_restaurant(
    group_id: uuid.UUID,
    data: RestaurantCreate,
    current_user: User = Depends(get_current_user),
    workflow: CreateRestaurantWorkflow = Depends(get_create_restaurant_workflow),
) -> RestaurantResponse:
    result = await workflow.execute(CreateRestaurantInput(group_id=group_id, data=data, current_user=current_user))
    return result.restaurant


@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
async def get_restaurant(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: GetRestaurantWorkflow = Depends(get_get_restaurant_workflow),
) -> RestaurantDetailResponse:
    result = await workflow.execute(
        GetRestaurantInput(group_id=group_id, restaurant_id=restaurant_id, current_user=current_user)
    )
    return result.restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    data: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    workflow: UpdateRestaurantWorkflow = Depends(get_update_restaurant_workflow),
) -> RestaurantResponse:
    result = await workflow.execute(
        UpdateRestaurantInput(group_id=group_id, restaurant_id=restaurant_id, data=data, current_user=current_user)
    )
    return result.restaurant


@router.delete("/{restaurant_id}", response_model=MessageResponse)
async def delete_restaurant(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: DeleteRestaurantWorkflow = Depends(get_delete_restaurant_workflow),
) -> MessageResponse:
    await workflow.execute(
        DeleteRestaurantInput(group_id=group_id, restaurant_id=restaurant_id, current_user=current_user)
    )
    return MessageResponse(message="Restaurant deleted successfully")


# --- Dish CRUD ---


@router.get("/{restaurant_id}/dishes", response_model=list[DishResponse])
async def list_dishes(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListDishesWorkflow = Depends(get_list_dishes_workflow),
) -> list[DishResponse]:
    result = await workflow.execute(
        ListDishesInput(group_id=group_id, restaurant_id=restaurant_id, current_user=current_user)
    )
    return result.dishes


@router.post("/{restaurant_id}/dishes", response_model=DishResponse, status_code=201)
async def create_dish(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    data: DishCreate,
    current_user: User = Depends(get_current_user),
    workflow: CreateDishWorkflow = Depends(get_create_dish_workflow),
) -> DishResponse:
    result = await workflow.execute(
        CreateDishInput(group_id=group_id, restaurant_id=restaurant_id, data=data, current_user=current_user)
    )
    return result.dish


@router.patch("/{restaurant_id}/dishes/{dish_id}", response_model=DishResponse)
async def update_dish(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    dish_id: uuid.UUID,
    data: DishUpdate,
    current_user: User = Depends(get_current_user),
    workflow: UpdateDishWorkflow = Depends(get_update_dish_workflow),
) -> DishResponse:
    result = await workflow.execute(
        UpdateDishInput(
            group_id=group_id,
            restaurant_id=restaurant_id,
            dish_id=dish_id,
            data=data,
            current_user=current_user,
        )
    )
    return result.dish


@router.delete("/{restaurant_id}/dishes/{dish_id}", response_model=MessageResponse)
async def delete_dish(
    group_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    dish_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: DeleteDishWorkflow = Depends(get_delete_dish_workflow),
) -> MessageResponse:
    await workflow.execute(
        DeleteDishInput(group_id=group_id, restaurant_id=restaurant_id, dish_id=dish_id, current_user=current_user)
    )
    return MessageResponse(message="Dish deleted successfully")
