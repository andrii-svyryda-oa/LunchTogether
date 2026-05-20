from pydantic import BaseModel

from app.core.exceptions import ValidationError
from app.core.security import hash_password
from app.repositories.password_reset import PasswordResetTokenRepository
from app.repositories.user import UserRepository
from app.schemas.internal import PasswordResetTokenMarkUsed
from app.schemas.user import PasswordResetConfirm


class ConfirmPasswordResetInput(BaseModel):
    data: PasswordResetConfirm


class ConfirmPasswordResetOutput(BaseModel):
    message: str


class ConfirmPasswordResetWorkflow:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: PasswordResetTokenRepository,
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository

    async def execute(self, input_data: ConfirmPasswordResetInput) -> ConfirmPasswordResetOutput:
        token_row = await self.token_repository.get_active_by_token(input_data.data.token)
        if token_row is None:
            raise ValidationError(detail="Invalid or expired reset token")

        user = await self.user_repository.get_by_id(token_row.user_id)
        if user is None or not user.is_active:
            raise ValidationError(detail="Invalid or expired reset token")

        await self.user_repository.update_password(user.id, hash_password(input_data.data.new_password))
        await self.token_repository.update(token_row.id, PasswordResetTokenMarkUsed())

        return ConfirmPasswordResetOutput(message="Password reset successful")
