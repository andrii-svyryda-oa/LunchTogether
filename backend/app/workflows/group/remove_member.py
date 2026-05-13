import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import MembersScope, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository, GroupRepository


class RemoveMemberInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    member_user_id: uuid.UUID
    current_user: User


class RemoveMemberOutput(BaseModel):
    removed: bool


class RemoveMemberWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: RemoveMemberInput) -> RemoveMemberOutput:
        user = input_data.current_user

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if user.id != input_data.member_user_id:
            if not user.is_admin:
                membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
                if membership is None:
                    raise ForbiddenError(detail="You are not a member of this group")
                if membership.get_permission(PermissionType.MEMBERS) != MembersScope.EDITOR:
                    raise ForbiddenError(detail="You do not have permission to manage members")
            if group.owner_id == input_data.member_user_id:
                raise ForbiddenError(detail="Cannot modify the group owner")

        removed = await self.group_member_repository.delete_membership(
            input_data.member_user_id, input_data.group_id
        )
        return RemoveMemberOutput(removed=removed)
