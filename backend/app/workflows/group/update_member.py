import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.permissions import GROUP_ROLE_PRESETS
from app.models.enums import MembersScope, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository, GroupRepository
from app.repositories.user import UserRepository
from app.schemas.group import GroupMemberResponse, GroupMemberUpdate
from app.workflows.group.add_member import _build_member_response


class UpdateMemberInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    member_user_id: uuid.UUID
    data: GroupMemberUpdate
    current_user: User


class UpdateMemberOutput(BaseModel):
    member: GroupMemberResponse


class UpdateMemberWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        user_repository: UserRepository,
        permission_repository: GroupMemberPermissionRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.user_repository = user_repository
        self.permission_repository = permission_repository

    async def execute(self, input_data: UpdateMemberInput) -> UpdateMemberOutput:
        user = input_data.current_user

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            if membership.get_permission(PermissionType.MEMBERS) != MembersScope.EDITOR:
                raise ForbiddenError(detail="You do not have permission to manage members")

        if group.owner_id == input_data.member_user_id:
            raise ForbiddenError(detail="Cannot modify the group owner")

        target_membership = await self.group_member_repository.get_membership(
            input_data.member_user_id, input_data.group_id
        )
        if target_membership is None:
            raise NotFoundError(detail="Member not found in this group")

        permissions_data: dict[str, str] = {}

        if input_data.data.role is not None:
            role_presets = GROUP_ROLE_PRESETS[input_data.data.role]
            permissions_data = {pt.value: level for pt, level in role_presets.items()}

        if input_data.data.permissions:
            for perm in input_data.data.permissions:
                permissions_data[perm.permission_type.value] = perm.level

        if permissions_data:
            await self.permission_repository.set_permissions(target_membership.id, permissions_data)

        member = await self.group_member_repository.get_membership(input_data.member_user_id, input_data.group_id)
        target_user = await self.user_repository.get_by_id(input_data.member_user_id)

        return UpdateMemberOutput(member=_build_member_response(member, target_user))
