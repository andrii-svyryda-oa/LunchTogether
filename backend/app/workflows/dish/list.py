import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import DishRepository
from app.schemas.restaurant import DishResponse


class ListDishesInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    restaurant_id: uuid.UUID
    current_user: User


class ListDishesOutput(BaseModel):
    dishes: list[DishResponse]


class ListDishesWorkflow:
    def __init__(
        self,
        dish_repository: DishRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.dish_repository = dish_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: ListDishesInput) -> ListDishesOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        dishes = await self.dish_repository.get_by_restaurant(input_data.restaurant_id)
        return ListDishesOutput(dishes=[DishResponse.model_validate(d) for d in dishes])
