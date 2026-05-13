from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.models.enums import InvitationStatus
from app.repositories.group import GroupInvitationRepository
from app.repositories.user import UserRepository
from app.schemas.group import InvitationPreviewResponse


class PreviewByTokenInput(BaseModel):
    token: str


class PreviewByTokenOutput(BaseModel):
    preview: InvitationPreviewResponse


class PreviewByTokenWorkflow:
    def __init__(
        self,
        invitation_repository: GroupInvitationRepository,
        user_repository: UserRepository,
    ):
        self.invitation_repository = invitation_repository
        self.user_repository = user_repository

    async def execute(self, input_data: PreviewByTokenInput) -> PreviewByTokenOutput:
        invitation = await self.invitation_repository.get_by_token_with_relations(input_data.token)
        if invitation is None or invitation.status != InvitationStatus.PENDING:
            raise NotFoundError(detail="Invitation not found or no longer valid")

        invitee_has_account = await self.user_repository.get_by_email(invitation.invitee_email) is not None

        return PreviewByTokenOutput(
            preview=InvitationPreviewResponse(
                group_id=invitation.group_id,
                group_name=invitation.group.name,
                group_logo_path=invitation.group.logo_path,
                inviter_full_name=invitation.inviter.full_name,
                inviter_email=invitation.inviter.email,
                invitee_email=invitation.invitee_email,
                invitee_has_account=invitee_has_account,
            )
        )
