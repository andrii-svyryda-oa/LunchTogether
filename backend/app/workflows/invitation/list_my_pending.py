from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.repositories.group import GroupInvitationRepository
from app.schemas.group import MyInvitationResponse


class ListMyPendingInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    current_user: User


class ListMyPendingOutput(BaseModel):
    invitations: list[MyInvitationResponse]


class ListMyPendingWorkflow:
    def __init__(self, invitation_repository: GroupInvitationRepository):
        self.invitation_repository = invitation_repository

    async def execute(self, input_data: ListMyPendingInput) -> ListMyPendingOutput:
        user = input_data.current_user
        invitations = await self.invitation_repository.get_pending_for_user(user.id, user.email)
        result = []
        for inv in invitations:
            group = getattr(inv, "group", None)
            inviter = getattr(inv, "inviter", None)
            result.append(
                MyInvitationResponse(
                    id=inv.id,
                    group_id=inv.group_id,
                    group_name=group.name if group else "Unknown group",
                    group_logo_path=group.logo_path if group else None,
                    inviter_full_name=inviter.full_name if inviter else None,
                    invitee_email=inv.invitee_email,
                    status=inv.status,
                    token=inv.token,
                    created_at=inv.created_at,
                )
            )
        return ListMyPendingOutput(invitations=result)
