from pydantic import BaseModel

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.repositories.user import UserRepository
from app.schemas.internal import UserInternalCreate
from app.schemas.user import AdminUserCreate, UserResponse


class CreateUserInput(BaseModel):
    data: AdminUserCreate


class CreateUserOutput(BaseModel):
    user: UserResponse


class CreateUserWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        if await self.user_repository.exists_by_email(input_data.data.email):
            raise ConflictError(detail="User with this email already exists")

        user = await self.user_repository.create(
            UserInternalCreate(
                email=input_data.data.email,
                hashed_password=hash_password(input_data.data.password),
                full_name=input_data.data.full_name,
                role=input_data.data.role,
            )
        )
        return CreateUserOutput(user=UserResponse.model_validate(user))
