from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.permissions import GROUP_ROLE_PRESETS
from app.models.enums import GroupRole, InvitationStatus
from app.models.user import User
from app.repositories.group import GroupInvitationRepository, GroupMemberPermissionRepository, GroupMemberRepository
from app.schemas.group import InvitationAcceptResponse
from app.schemas.internal import GroupInvitationStatusUpdate, GroupMemberInternalCreate


class AcceptInvitationInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    token: str
    current_user: User


class AcceptInvitationOutput(BaseModel):
    result: InvitationAcceptResponse


class AcceptInvitationWorkflow:
    def __init__(
        self,
        invitation_repository: GroupInvitationRepository,
        group_member_repository: GroupMemberRepository,
        permission_repository: GroupMemberPermissionRepository,
    ):
        self.invitation_repository = invitation_repository
        self.group_member_repository = group_member_repository
        self.permission_repository = permission_repository

    async def execute(self, input_data: AcceptInvitationInput) -> AcceptInvitationOutput:
        user = input_data.current_user

        invitation = await self.invitation_repository.get_by_token(input_data.token)
        if invitation is None:
            raise NotFoundError(detail="Invitation not found")

        if invitation.status != InvitationStatus.PENDING:
            raise ForbiddenError(detail="Invitation is no longer valid")

        if invitation.invitee_id and invitation.invitee_id != user.id:
            raise ForbiddenError(detail="This invitation is not for you")

        if invitation.invitee_email != user.email:
            raise ForbiddenError(detail="This invitation is not for your email address")

        member_count = await self.group_member_repository.count_members(invitation.group_id)
        if member_count >= 25:
            raise ForbiddenError(detail="Group has reached the maximum of 25 members")

        member = await self.group_member_repository.create(
            GroupMemberInternalCreate(user_id=user.id, group_id=invitation.group_id)
        )

        member_presets = GROUP_ROLE_PRESETS[GroupRole.MEMBER]
        await self.permission_repository.set_permissions(
            member.id,
            {pt.value: level for pt, level in member_presets.items()},
        )

        await self.invitation_repository.update(
            invitation.id, GroupInvitationStatusUpdate(status=InvitationStatus.ACCEPTED)
        )

        return AcceptInvitationOutput(
            result=InvitationAcceptResponse(
                message="Successfully joined the group",
                group_id=invitation.group_id,
            )
        )
