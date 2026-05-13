from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import InvitationStatus
from app.models.user import User
from app.repositories.group import GroupInvitationRepository
from app.schemas.internal import GroupInvitationStatusUpdate


class DeclineInvitationInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    token: str
    current_user: User


class DeclineInvitationOutput(BaseModel):
    pass


class DeclineInvitationWorkflow:
    def __init__(self, invitation_repository: GroupInvitationRepository):
        self.invitation_repository = invitation_repository

    async def execute(self, input_data: DeclineInvitationInput) -> DeclineInvitationOutput:
        user = input_data.current_user

        invitation = await self.invitation_repository.get_by_token(input_data.token)
        if invitation is None:
            raise NotFoundError(detail="Invitation not found")

        if invitation.status != InvitationStatus.PENDING:
            raise ForbiddenError(detail="Invitation is no longer valid")

        if invitation.invitee_email != user.email:
            raise ForbiddenError(detail="This invitation is not for your email address")

        await self.invitation_repository.update(
            invitation.id, GroupInvitationStatusUpdate(status=InvitationStatus.DECLINED)
        )

        return DeclineInvitationOutput()
