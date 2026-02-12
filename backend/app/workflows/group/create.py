from pydantic import BaseModel

from app.core.exceptions import ForbiddenError
from app.models.enums import GROUP_ROLE_PRESETS, GroupRole
from app.models.user import User
from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository, GroupRepository
from app.schemas.group import GroupCreate, GroupResponse


class CreateGroupInput(BaseModel):
    data: GroupCreate
    current_user: object  # User model

    class Config:
        arbitrary_types_allowed = True


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
        user: User = input_data.current_user  # type: ignore[assignment]

        # Check group limit (admins bypass)
        if not user.is_admin:
            count = await self.group_repository.count_by_owner(user.id)
            if count >= MAX_GROUPS_PER_USER:
                raise ForbiddenError(detail=f"You can create a maximum of {MAX_GROUPS_PER_USER} groups")

        # Create the group
        group = await self.group_repository.create(
            {
                "name": input_data.data.name,
                "description": input_data.data.description,
                "owner_id": user.id,
            }
        )

        # Add the creator as a member with Admin role
        member = await self.group_member_repository.create(
            {
                "user_id": user.id,
                "group_id": group.id,
            }
        )

        # Set Admin role permissions
        admin_presets = GROUP_ROLE_PRESETS[GroupRole.ADMIN]
        await self.permission_repository.set_permissions(
            member.id,
            {pt.value: level for pt, level in admin_presets.items()},
        )

        return CreateGroupOutput(group=GroupResponse.model_validate(group))
