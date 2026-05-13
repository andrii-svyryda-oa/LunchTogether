import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import InvitationStatus, MembersScope, PermissionType
from app.models.group import Group, GroupInvitation
from app.models.user import User
from app.repositories.group import GroupInvitationRepository, GroupMemberRepository, GroupRepository


class CancelInvitationInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    invitation_id: uuid.UUID
    current_user: User


class CancelInvitationOutput(BaseModel):
    pass


class CancelInvitationWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        invitation_repository: GroupInvitationRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.invitation_repository = invitation_repository

    async def _can_cancel(self, user: User, group: Group, invitation: GroupInvitation) -> bool:
        if user.is_admin:
            return True
        if group.owner_id == user.id:
            return True
        if invitation.inviter_id == user.id:
            return True
        membership = await self.group_member_repository.get_membership(user.id, group.id)
        return membership is not None and membership.get_permission(PermissionType.MEMBERS) == MembersScope.EDITOR

    async def execute(self, input_data: CancelInvitationInput) -> CancelInvitationOutput:
        user = input_data.current_user

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        invitation = await self.invitation_repository.get_by_id(input_data.invitation_id)
        if invitation is None or invitation.group_id != input_data.group_id:
            raise NotFoundError(detail="Invitation not found")

        if invitation.status != InvitationStatus.PENDING:
            raise ForbiddenError(detail="Only pending invitations can be cancelled")

        if not await self._can_cancel(user, group, invitation):
            raise ForbiddenError(detail="You do not have permission to cancel this invitation")

        await self.invitation_repository.delete(invitation.id)

        return CancelInvitationOutput()
