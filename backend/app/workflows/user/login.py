from pydantic import BaseModel

from app.core.exceptions import AuthError
from app.core.security import create_access_token, verify_password
from app.repositories.user import UserRepository
from app.schemas.user import UserLogin, UserResponse


class LoginInput(BaseModel):
    data: UserLogin


class LoginOutput(BaseModel):
    access_token: str
    user: UserResponse


class LoginWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: LoginInput) -> LoginOutput:
        # Find user by email
        user = await self.user_repository.get_by_email(input_data.data.email)
        if user is None:
            raise AuthError(detail="Invalid email or password")

        # Verify password
        if not verify_password(input_data.data.password, user.hashed_password):
            raise AuthError(detail="Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise AuthError(detail="User account is deactivated")

        # Generate JWT token
        access_token = create_access_token(subject=str(user.id))

        return LoginOutput(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
