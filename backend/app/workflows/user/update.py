import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate


class UpdateUserInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: uuid.UUID
    data: UserUpdate
    current_user: User


class UpdateUserOutput(BaseModel):
    user: UserResponse


class UpdateUserWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: UpdateUserInput) -> UpdateUserOutput:
        if input_data.current_user.id != input_data.user_id and input_data.current_user.role != UserRole.ADMIN:
            raise ForbiddenError(detail="You can only update your own profile")

        if not input_data.data.model_dump(exclude_unset=True):
            user = await self.user_repository.get_by_id(input_data.user_id)
            if user is None:
                raise NotFoundError(detail="User not found")
            return UpdateUserOutput(user=UserResponse.model_validate(user))

        user = await self.user_repository.update(input_data.user_id, input_data.data)
        if user is None:
            raise NotFoundError(detail="User not found")
        return UpdateUserOutput(user=UserResponse.model_validate(user))
