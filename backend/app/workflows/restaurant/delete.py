import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import PermissionType, RestaurantsScope
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.repositories.restaurant import RestaurantRepository


class DeleteRestaurantInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    restaurant_id: uuid.UUID
    current_user: User


class DeleteRestaurantOutput(BaseModel):
    deleted: bool


class DeleteRestaurantWorkflow:
    def __init__(
        self,
        restaurant_repository: RestaurantRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.restaurant_repository = restaurant_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: DeleteRestaurantInput) -> DeleteRestaurantOutput:
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

        deleted = await self.restaurant_repository.delete(input_data.restaurant_id)
        return DeleteRestaurantOutput(deleted=deleted)
