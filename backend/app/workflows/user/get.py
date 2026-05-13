import uuid

from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse


class GetUserInput(BaseModel):
    user_id: uuid.UUID


class GetUserOutput(BaseModel):
    user: UserResponse


class GetUserWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: GetUserInput) -> GetUserOutput:
        user = await self.user_repository.get_by_id(input_data.user_id)
        if user is None:
            raise NotFoundError(detail="User not found")
        return GetUserOutput(user=UserResponse.model_validate(user))
