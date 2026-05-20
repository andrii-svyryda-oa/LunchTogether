import logging
import secrets
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel

from app.core.email import EmailService
from app.repositories.password_reset import PasswordResetTokenRepository
from app.repositories.user import UserRepository
from app.schemas.internal import PasswordResetTokenInternalCreate
from app.schemas.user import PasswordResetRequest

logger = logging.getLogger(__name__)

RESET_TOKEN_TTL = timedelta(hours=1)


class RequestPasswordResetInput(BaseModel):
    data: PasswordResetRequest


class RequestPasswordResetOutput(BaseModel):
    message: str


class RequestPasswordResetWorkflow:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: PasswordResetTokenRepository,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.email_service = email_service

    async def execute(self, input_data: RequestPasswordResetInput) -> RequestPasswordResetOutput:
        # Don't reveal whether the email exists.
        generic_message = "If an account with that email exists, a reset link has been sent."

        user = await self.user_repository.get_by_email(input_data.data.email)
        if user is None or not user.is_active:
            return RequestPasswordResetOutput(message=generic_message)

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + RESET_TOKEN_TTL

        await self.token_repository.create(
            PasswordResetTokenInternalCreate(
                user_id=user.id,
                token=token,
                expires_at=expires_at,
            )
        )

        try:
            await self.email_service.send_password_reset_email(
                to_email=user.email,
                user_name=user.full_name,
                token=token,
            )
        except Exception:
            logger.exception("Failed to send password reset email to %s", user.email)

        return RequestPasswordResetOutput(message=generic_message)
