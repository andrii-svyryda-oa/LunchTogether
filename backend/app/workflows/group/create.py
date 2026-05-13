from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.core.permissions import GROUP_ROLE_PRESETS
from app.models.enums import GroupRole
from app.models.user import User
from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository, GroupRepository
from app.schemas.group import GroupCreate, GroupResponse
from app.schemas.internal import GroupInternalCreate, GroupMemberInternalCreate


class CreateGroupInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: GroupCreate
    current_user: User


class CreateGroupOutput(BaseModel):
    group: GroupResponse


MAX_GROUPS_PER_USER = 5


class CreateGroupWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        permission_repository: GroupMemberPermissionRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.permission_repository = permission_repository

    async def execute(self, input_data: CreateGroupInput) -> CreateGroupOutput:
        user = input_data.current_user

        # Check group limit (admins bypass)
        if not user.is_admin:
            count = await self.group_repository.count_by_owner(user.id)
            if count >= MAX_GROUPS_PER_USER:
                raise ForbiddenError(detail=f"You can create a maximum of {MAX_GROUPS_PER_USER} groups")

        # Create the group
        group = await self.group_repository.create(
            GroupInternalCreate(
                name=input_data.data.name,
                description=input_data.data.description,
                owner_id=user.id,
            )
        )

        # Add the creator as a member with Admin role
        member = await self.group_member_repository.create(
            GroupMemberInternalCreate(user_id=user.id, group_id=group.id)
        )

        # Set Admin role permissions
        admin_presets = GROUP_ROLE_PRESETS[GroupRole.ADMIN]
        await self.permission_repository.set_permissions(
            member.id,
            {pt.value: level for pt, level in admin_presets.items()},
        )

        return CreateGroupOutput(group=GroupResponse.model_validate(group))
