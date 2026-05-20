import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.enums import PermissionType, RestaurantsScope
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.internal import RestaurantInternalCreate
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse


class CreateRestaurantInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    data: RestaurantCreate
    current_user: User


class CreateRestaurantOutput(BaseModel):
    restaurant: RestaurantResponse


class CreateRestaurantWorkflow:
    def __init__(
        self,
        restaurant_repository: RestaurantRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.restaurant_repository = restaurant_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: CreateRestaurantInput) -> CreateRestaurantOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            if membership.get_permission(PermissionType.RESTAURANTS) != RestaurantsScope.EDITOR:
                raise ForbiddenError(detail="You do not have permission to manage restaurants")

        restaurant = await self.restaurant_repository.create(
            RestaurantInternalCreate(
                name=input_data.data.name,
                description=input_data.data.description,
                menu_url=input_data.data.menu_url,
                group_id=input_data.group_id,
            )
        )
        return CreateRestaurantOutput(restaurant=RestaurantResponse.model_validate(restaurant))
