import logging
import secrets
import uuid

from pydantic import BaseModel

from app.core.email import EmailService
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.enums import GROUP_ROLE_PRESETS, GroupRole, InvitationStatus, MembersScope, PermissionType
from app.models.group import Group, GroupInvitation
from app.models.user import User
from app.repositories.group import (
    GroupInvitationRepository,
    GroupMemberPermissionRepository,
    GroupMemberRepository,
    GroupRepository,
)
from app.repositories.user import UserRepository
from app.schemas.group import InvitationAcceptResponse, InvitationCreate, InvitationResponse

logger = logging.getLogger(__name__)


class InviteInput(BaseModel):
    group_id: uuid.UUID
    data: InvitationCreate
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class InviteOutput(BaseModel):
    invitation: InvitationResponse


class AcceptInviteInput(BaseModel):
    token: str
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class AcceptInviteOutput(BaseModel):
    result: InvitationAcceptResponse


class ListInvitationsInput(BaseModel):
    group_id: uuid.UUID
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class ListInvitationsOutput(BaseModel):
    invitations: list[InvitationResponse]


class CancelInvitationInput(BaseModel):
    group_id: uuid.UUID
    invitation_id: uuid.UUID
    current_user: object

    class Config:
        arbitrary_types_allowed = True


def _build_invitation_response(invitation: GroupInvitation) -> InvitationResponse:
    """Build an InvitationResponse with inviter info if loaded."""
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


class InviteWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        invitation_repository: GroupInvitationRepository,
        user_repository: UserRepository,
        permission_repository: GroupMemberPermissionRepository,
        email_service: EmailService,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.invitation_repository = invitation_repository
        self.user_repository = user_repository
        self.permission_repository = permission_repository
        self.email_service = email_service

    async def create_invitation(self, input_data: InviteInput) -> InviteOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        # Check current user is a member
        membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
        if membership is None and not user.is_admin:
            raise ForbiddenError(detail="You are not a member of this group")

        # Check if already pending invitation for this email
        existing = await self.invitation_repository.get_pending_for_email(input_data.data.email, input_data.group_id)
        if existing is not None:
            raise ConflictError(detail="An invitation is already pending for this email")

        # Check if already a member (look up by email)
        invitee = await self.user_repository.get_by_email(input_data.data.email)
        if invitee is not None:
            existing_member = await self.group_member_repository.get_membership(invitee.id, input_data.group_id)
            if existing_member is not None:
                raise ConflictError(detail="This user is already a member of the group")

        token = secrets.token_urlsafe(32)

        invitation = await self.invitation_repository.create(
            {
                "group_id": input_data.group_id,
                "inviter_id": user.id,
                "invitee_email": input_data.data.email,
                "invitee_id": invitee.id if invitee else None,
                "status": InvitationStatus.PENDING,
                "token": token,
            }
        )

        # Send invitation email (fire-and-forget, don't block on failure)
        try:
            await self.email_service.send_invitation_email(
                to_email=input_data.data.email,
                inviter_name=user.full_name,
                group_name=group.name,
                token=token,
            )
        except Exception:
            logger.exception("Failed to send invitation email to %s", input_data.data.email)

        return InviteOutput(invitation=InvitationResponse.model_validate(invitation))

    async def accept_invitation(self, input_data: AcceptInviteInput) -> AcceptInviteOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        invitation = await self.invitation_repository.get_by_token(input_data.token)
        if invitation is None:
            raise NotFoundError(detail="Invitation not found")

        if invitation.status != InvitationStatus.PENDING:
            raise ForbiddenError(detail="Invitation is no longer valid")

        # Verify the current user matches the invitation
        if invitation.invitee_id and invitation.invitee_id != user.id:
            raise ForbiddenError(detail="This invitation is not for you")

        if invitation.invitee_email != user.email:
            raise ForbiddenError(detail="This invitation is not for your email address")

        # Check member limit
        member_count = await self.group_member_repository.count_members(invitation.group_id)
        if member_count >= 25:
            raise ForbiddenError(detail="Group has reached the maximum of 25 members")

        # Add user to group with default Member role
        member = await self.group_member_repository.create(
            {
                "user_id": user.id,
                "group_id": invitation.group_id,
            }
        )

        # Set Member role permissions
        member_presets = GROUP_ROLE_PRESETS[GroupRole.MEMBER]
        await self.permission_repository.set_permissions(
            member.id,
            {pt.value: level for pt, level in member_presets.items()},
        )

        # Update invitation status
        await self.invitation_repository.update(invitation.id, {"status": InvitationStatus.ACCEPTED})

        return AcceptInviteOutput(
            result=InvitationAcceptResponse(
                message="Successfully joined the group",
                group_id=invitation.group_id,
            )
        )

    async def decline_invitation(self, token: str, user: User) -> None:
        invitation = await self.invitation_repository.get_by_token(token)
        if invitation is None:
            raise NotFoundError(detail="Invitation not found")

        if invitation.status != InvitationStatus.PENDING:
            raise ForbiddenError(detail="Invitation is no longer valid")

        await self.invitation_repository.update(invitation.id, {"status": InvitationStatus.DECLINED})

    async def list_pending_invitations(self, input_data: ListInvitationsInput) -> ListInvitationsOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        invitations = await self.invitation_repository.get_pending_for_group(input_data.group_id)
        return ListInvitationsOutput(
            invitations=[_build_invitation_response(inv) for inv in invitations],
        )

    async def _can_cancel(self, user: User, group: Group, invitation: GroupInvitation) -> bool:
        if user.is_admin:
            return True
        if group.owner_id == user.id:
            return True
        if invitation.inviter_id == user.id:
            return True
        membership = await self.group_member_repository.get_membership(user.id, group.id)
        if membership is not None and membership.get_permission(PermissionType.MEMBERS) == MembersScope.EDITOR:
            return True
        return False

    async def cancel_invitation(self, input_data: CancelInvitationInput) -> None:
        user: User = input_data.current_user  # type: ignore[assignment]

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
