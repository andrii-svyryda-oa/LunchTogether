import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import PermissionType, RestaurantsScope
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import DishRepository
from app.schemas.restaurant import DishResponse, DishUpdate


class UpdateDishInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    restaurant_id: uuid.UUID
    dish_id: uuid.UUID
    data: DishUpdate
    current_user: User


class UpdateDishOutput(BaseModel):
    dish: DishResponse


class UpdateDishWorkflow:
    def __init__(
        self,
        dish_repository: DishRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.dish_repository = dish_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: UpdateDishInput) -> UpdateDishOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            if membership.get_permission(PermissionType.RESTAURANTS) != RestaurantsScope.EDITOR:
                raise ForbiddenError(detail="You do not have permission to manage restaurants")

        dish = await self.dish_repository.get_by_id(input_data.dish_id)
        if dish is None or dish.restaurant_id != input_data.restaurant_id:
            raise NotFoundError(detail="Dish not found")

        if not input_data.data.model_dump(exclude_unset=True):
            return UpdateDishOutput(dish=DishResponse.model_validate(dish))

        updated = await self.dish_repository.update(input_data.dish_id, input_data.data)
        return UpdateDishOutput(dish=DishResponse.model_validate(updated))
