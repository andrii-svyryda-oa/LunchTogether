from pydantic import BaseModel

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.repositories.group import GroupInvitationRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse


class RegisterInput(BaseModel):
    data: UserCreate


class RegisterOutput(BaseModel):
    user: UserResponse


class RegisterWorkflow:
    def __init__(
        self,
        user_repository: UserRepository,
        invitation_repository: GroupInvitationRepository | None = None,
    ):
        self.user_repository = user_repository
        self.invitation_repository = invitation_repository

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

        # Back-fill invitee_id on any invitations that were sent before this account existed
        if self.invitation_repository is not None:
            await self.invitation_repository.link_invitations_to_user(user.id, user.email)

        return RegisterOutput(user=UserResponse.model_validate(user))
