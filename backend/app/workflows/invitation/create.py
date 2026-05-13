import logging
import secrets
import uuid

from pydantic import BaseModel, ConfigDict

from app.core.email import EmailService
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.enums import InvitationStatus
from app.models.user import User
from app.repositories.group import GroupInvitationRepository, GroupMemberRepository, GroupRepository
from app.repositories.user import UserRepository
from app.schemas.group import InvitationCreate, InvitationResponse
from app.schemas.internal import GroupInvitationInternalCreate

logger = logging.getLogger(__name__)


class CreateInvitationInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    data: InvitationCreate
    current_user: User


class CreateInvitationOutput(BaseModel):
    invitation: InvitationResponse


class CreateInvitationWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        invitation_repository: GroupInvitationRepository,
        user_repository: UserRepository,
        email_service: EmailService,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.invitation_repository = invitation_repository
        self.user_repository = user_repository
        self.email_service = email_service

    async def execute(self, input_data: CreateInvitationInput) -> CreateInvitationOutput:
        user = input_data.current_user

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
        if membership is None and not user.is_admin:
            raise ForbiddenError(detail="You are not a member of this group")

        existing = await self.invitation_repository.get_pending_for_email(input_data.data.email, input_data.group_id)
        if existing is not None:
            raise ConflictError(detail="An invitation is already pending for this email")

        invitee = await self.user_repository.get_by_email(input_data.data.email)
        if invitee is not None:
            existing_member = await self.group_member_repository.get_membership(invitee.id, input_data.group_id)
            if existing_member is not None:
                raise ConflictError(detail="This user is already a member of the group")

        token = secrets.token_urlsafe(32)

        invitation = await self.invitation_repository.create(
            GroupInvitationInternalCreate(
                group_id=input_data.group_id,
                inviter_id=user.id,
                invitee_email=input_data.data.email,
                invitee_id=invitee.id if invitee else None,
                status=InvitationStatus.PENDING,
                token=token,
            )
        )

        try:
            await self.email_service.send_invitation_email(
                to_email=input_data.data.email,
                inviter_name=user.full_name,
                group_name=group.name,
                token=token,
            )
        except Exception:
            logger.exception("Failed to send invitation email to %s", input_data.data.email)

        return CreateInvitationOutput(invitation=InvitationResponse.model_validate(invitation))
