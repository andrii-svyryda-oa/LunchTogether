import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.group import GroupInvitation
from app.models.user import User
from app.repositories.group import GroupInvitationRepository, GroupMemberRepository, GroupRepository
from app.schemas.group import InvitationResponse


def _build_invitation_response(invitation: GroupInvitation) -> InvitationResponse:
    inviter = getattr(invitation, "inviter", None)
    return InvitationResponse(
        id=invitation.id,
        group_id=invitation.group_id,
        inviter_id=invitation.inviter_id,
        invitee_email=invitation.invitee_email,
        invitee_id=invitation.invitee_id,
        status=invitation.status,
        token=invitation.token,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
        inviter_full_name=inviter.full_name if inviter else None,
        inviter_email=inviter.email if inviter else None,
    )


class ListPendingForGroupInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class ListPendingForGroupOutput(BaseModel):
    invitations: list[InvitationResponse]


class ListPendingForGroupWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        invitation_repository: GroupInvitationRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.invitation_repository = invitation_repository

    async def execute(self, input_data: ListPendingForGroupInput) -> ListPendingForGroupOutput:
        user = input_data.current_user

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        invitations = await self.invitation_repository.get_pending_for_group(input_data.group_id)
        return ListPendingForGroupOutput(invitations=[_build_invitation_response(inv) for inv in invitations])
