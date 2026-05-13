import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import PermissionType, RestaurantsScope
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import DishRepository, RestaurantRepository
from app.schemas.internal import DishInternalCreate
from app.schemas.restaurant import DishCreate, DishResponse


class CreateDishInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    restaurant_id: uuid.UUID
    data: DishCreate
    current_user: User


class CreateDishOutput(BaseModel):
    dish: DishResponse


class CreateDishWorkflow:
    def __init__(
        self,
        dish_repository: DishRepository,
        restaurant_repository: RestaurantRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.dish_repository = dish_repository
        self.restaurant_repository = restaurant_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: CreateDishInput) -> CreateDishOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            if membership.get_permission(PermissionType.RESTAURANTS) != RestaurantsScope.EDITOR:
                raise ForbiddenError(detail="You do not have permission to manage restaurants")

        restaurant = await self.restaurant_repository.get_by_id(input_data.restaurant_id)
        if restaurant is None or restaurant.group_id != input_data.group_id:
            raise NotFoundError(detail="Restaurant not found")

        dish = await self.dish_repository.create(
            DishInternalCreate(
                name=input_data.data.name,
                detail=input_data.data.detail,
                price=input_data.data.price,
                restaurant_id=input_data.restaurant_id,
            )
        )
        return CreateDishOutput(dish=DishResponse.model_validate(dish))
