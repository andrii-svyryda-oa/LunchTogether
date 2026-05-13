import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import MembersScope, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository, GroupRepository
from app.schemas.group import GroupMemberResponse, PermissionCreate
from app.workflows.group.add_member import _build_member_response


class SetMemberPermissionsInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    member_user_id: uuid.UUID
    permissions: list[PermissionCreate]
    current_user: User


class SetMemberPermissionsOutput(BaseModel):
    member: GroupMemberResponse


class SetMemberPermissionsWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        permission_repository: GroupMemberPermissionRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.permission_repository = permission_repository

    async def execute(self, input_data: SetMemberPermissionsInput) -> SetMemberPermissionsOutput:
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

        target_membership = await self.group_member_repository.get_membership(
            input_data.member_user_id, input_data.group_id
        )
        if target_membership is None:
            raise NotFoundError(detail="Member not found in this group")

        permissions_data = {p.permission_type.value: p.level for p in input_data.permissions}
        await self.permission_repository.set_permissions(target_membership.id, permissions_data)

        member = await self.group_member_repository.get_membership(input_data.member_user_id, input_data.group_id)
        return SetMemberPermissionsOutput(member=_build_member_response(member))
