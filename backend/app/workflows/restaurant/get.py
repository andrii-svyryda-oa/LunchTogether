import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.restaurant import DishResponse, RestaurantDetailResponse, RestaurantResponse


class GetRestaurantInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    restaurant_id: uuid.UUID
    current_user: User


class GetRestaurantOutput(BaseModel):
    restaurant: RestaurantDetailResponse


class GetRestaurantWorkflow:
    def __init__(
        self,
        restaurant_repository: RestaurantRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.restaurant_repository = restaurant_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: GetRestaurantInput) -> GetRestaurantOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        restaurant = await self.restaurant_repository.get_with_dishes(input_data.restaurant_id)
        if restaurant is None or restaurant.group_id != input_data.group_id:
            raise NotFoundError(detail="Restaurant not found")

        dishes = [DishResponse.model_validate(d) for d in restaurant.dishes]
        detail = RestaurantDetailResponse(
            **{k: getattr(restaurant, k) for k in RestaurantResponse.model_fields if hasattr(restaurant, k)},
            dishes=dishes,
        )
        return GetRestaurantOutput(restaurant=detail)
