from pydantic import BaseModel

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.repositories.group import GroupInvitationRepository
from app.repositories.user import UserRepository
from app.schemas.internal import UserInternalCreate
from app.schemas.user import UserCreate, UserResponse
from app.workflows.invitation.link_to_user import LinkInvitationsToUserInput, LinkInvitationsToUserWorkflow


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
        self.link_workflow = (
            LinkInvitationsToUserWorkflow(invitation_repository) if invitation_repository is not None else None
        )

    async def execute(self, input_data: RegisterInput) -> RegisterOutput:
        if await self.user_repository.exists_by_email(input_data.data.email):
            raise ConflictError(detail="User with this email already exists")

        user = await self.user_repository.create(
            UserInternalCreate(
                email=input_data.data.email,
                hashed_password=hash_password(input_data.data.password),
                full_name=input_data.data.full_name,
            )
        )

        if self.link_workflow is not None:
            await self.link_workflow.execute(
                LinkInvitationsToUserInput(user_id=user.id, user_email=user.email)
            )

        return RegisterOutput(user=UserResponse.model_validate(user))
