from pydantic import BaseModel

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse


class RegisterInput(BaseModel):
    data: UserCreate


class RegisterOutput(BaseModel):
    user: UserResponse


class RegisterWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: RegisterInput) -> RegisterOutput:
        # Check if email already exists
        if await self.user_repository.exists_by_email(input_data.data.email):
            raise ConflictError(detail="User with this email already exists")

        # Hash password and create user
        user = await self.user_repository.create(
            {
                "email": input_data.data.email,
                "hashed_password": hash_password(input_data.data.password),
                "full_name": input_data.data.full_name,
            }
        )

        return RegisterOutput(user=UserResponse.model_validate(user))
