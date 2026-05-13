import uuid

from pydantic import BaseModel

from app.repositories.group import GroupInvitationRepository


class LinkInvitationsToUserInput(BaseModel):
    user_id: uuid.UUID
    user_email: str


class LinkInvitationsToUserOutput(BaseModel):
    pass


class LinkInvitationsToUserWorkflow:
    def __init__(self, invitation_repository: GroupInvitationRepository):
        self.invitation_repository = invitation_repository

    async def execute(self, input_data: LinkInvitationsToUserInput) -> LinkInvitationsToUserOutput:
        await self.invitation_repository.link_invitations_to_user(input_data.user_id, input_data.user_email)
        return LinkInvitationsToUserOutput()
