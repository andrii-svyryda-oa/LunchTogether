import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.restaurant import RestaurantResponse


class ListRestaurantsInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class ListRestaurantsOutput(BaseModel):
    restaurants: list[RestaurantResponse]


class ListRestaurantsWorkflow:
    def __init__(
        self,
        restaurant_repository: RestaurantRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.restaurant_repository = restaurant_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: ListRestaurantsInput) -> ListRestaurantsOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        restaurants = await self.restaurant_repository.get_by_group(input_data.group_id)
        return ListRestaurantsOutput(restaurants=[RestaurantResponse.model_validate(r) for r in restaurants])
