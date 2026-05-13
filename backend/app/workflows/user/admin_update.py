import uuid

from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.repositories.user import UserRepository
from app.schemas.user import AdminUserUpdate, UserResponse


class AdminUpdateUserInput(BaseModel):
    user_id: uuid.UUID
    data: AdminUserUpdate


class AdminUpdateUserOutput(BaseModel):
    user: UserResponse


class AdminUpdateUserWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: AdminUpdateUserInput) -> AdminUpdateUserOutput:
        if not input_data.data.model_dump(exclude_unset=True):
            user = await self.user_repository.get_by_id(input_data.user_id)
            if user is None:
                raise NotFoundError(detail="User not found")
            return AdminUpdateUserOutput(user=UserResponse.model_validate(user))

        user = await self.user_repository.update(input_data.user_id, input_data.data)
        if user is None:
            raise NotFoundError(detail="User not found")
        return AdminUpdateUserOutput(user=UserResponse.model_validate(user))
