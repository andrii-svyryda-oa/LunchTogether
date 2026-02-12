import uuid

from pydantic import BaseModel

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.enums import GROUP_ROLE_PRESETS, MembersScope, PermissionType
from app.models.group import Group
from app.models.user import User
from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository, GroupRepository
from app.repositories.user import UserRepository
from app.schemas.group import GroupMemberCreate, GroupMemberResponse, GroupMemberUpdate, PermissionResponse


class AddMemberInput(BaseModel):
    group_id: uuid.UUID
    data: GroupMemberCreate
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class AddMemberOutput(BaseModel):
    member: GroupMemberResponse


class UpdateMemberInput(BaseModel):
    group_id: uuid.UUID
    member_user_id: uuid.UUID
    data: GroupMemberUpdate
    current_user: object

    class Config:
        arbitrary_types_allowed = True


class UpdateMemberOutput(BaseModel):
    member: GroupMemberResponse


class RemoveMemberInput(BaseModel):
    group_id: uuid.UUID
    member_user_id: uuid.UUID
    current_user: object

    class Config:
        arbitrary_types_allowed = True


def _build_member_response(member, target_user=None) -> GroupMemberResponse:
    """Build a GroupMemberResponse from a GroupMember ORM object."""
    return GroupMemberResponse(
        id=member.id,
        user_id=member.user_id,
        group_id=member.group_id,
        permissions=[PermissionResponse(permission_type=p.permission_type, level=p.level) for p in member.permissions],
        created_at=member.created_at,
        updated_at=member.updated_at,
        user_full_name=target_user.full_name if target_user else (member.user.full_name if member.user else None),
        user_email=target_user.email if target_user else (member.user.email if member.user else None),
    )


class ManageMembersWorkflow:
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

    async def _check_editor_permission(self, user: User, group: Group, group_id: uuid.UUID) -> None:
        """Check that the current user has Members Editor permission."""
        if user.is_admin:
            return

        membership = await self.group_member_repository.get_membership(user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
        if membership.get_permission(PermissionType.MEMBERS) != MembersScope.EDITOR:
            raise ForbiddenError(detail="You do not have permission to manage members")

    async def _check_not_owner(self, group: Group, target_user_id: uuid.UUID) -> None:
        """Prevent actions on the group owner."""
        if group.owner_id == target_user_id:
            raise ForbiddenError(detail="Cannot modify the group owner")

    async def add_member(self, input_data: AddMemberInput) -> AddMemberOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        await self._check_editor_permission(user, group, input_data.group_id)

        # Check max members
        member_count = await self.group_member_repository.count_members(input_data.group_id)
        if member_count >= 25:
            raise ValidationError(detail="Group has reached the maximum of 25 members")

        # Check user exists
        target_user = await self.user_repository.get_by_id(input_data.data.user_id)
        if target_user is None:
            raise NotFoundError(detail="User not found")

        # Check not already a member
        existing = await self.group_member_repository.get_membership(input_data.data.user_id, input_data.group_id)
        if existing is not None:
            raise ConflictError(detail="User is already a member of this group")

        # Create the group member
        member = await self.group_member_repository.create(
            {
                "user_id": input_data.data.user_id,
                "group_id": input_data.group_id,
            }
        )

        # Build permissions from role preset
        role_presets = GROUP_ROLE_PRESETS[input_data.data.role]
        permissions_data = {pt.value: level for pt, level in role_presets.items()}

        # Apply optional permission overrides
        if input_data.data.permissions:
            for perm in input_data.data.permissions:
                permissions_data[perm.permission_type.value] = perm.level

        await self.permission_repository.set_permissions(member.id, permissions_data)

        # Reload member with permissions
        member = await self.group_member_repository.get_membership(input_data.data.user_id, input_data.group_id)

        return AddMemberOutput(member=_build_member_response(member, target_user))

    async def update_member(self, input_data: UpdateMemberInput) -> UpdateMemberOutput:
        user: User = input_data.current_user  # type: ignore[assignment]

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        await self._check_editor_permission(user, group, input_data.group_id)
        await self._check_not_owner(group, input_data.member_user_id)

        membership = await self.group_member_repository.get_membership(input_data.member_user_id, input_data.group_id)
        if membership is None:
            raise NotFoundError(detail="Member not found in this group")

        # Build permissions from role preset (if provided) + overrides
        permissions_data: dict[str, str] = {}

        if input_data.data.role is not None:
            role_presets = GROUP_ROLE_PRESETS[input_data.data.role]
            permissions_data = {pt.value: level for pt, level in role_presets.items()}

        # Apply individual permission overrides
        if input_data.data.permissions:
            for perm in input_data.data.permissions:
                permissions_data[perm.permission_type.value] = perm.level

        if permissions_data:
            await self.permission_repository.set_permissions(membership.id, permissions_data)

        # Reload member with updated permissions
        member = await self.group_member_repository.get_membership(input_data.member_user_id, input_data.group_id)
        target_user = await self.user_repository.get_by_id(input_data.member_user_id)

        return UpdateMemberOutput(member=_build_member_response(member, target_user))

    async def remove_member(self, input_data: RemoveMemberInput) -> bool:
        user: User = input_data.current_user  # type: ignore[assignment]

        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        # Users can always remove themselves
        if user.id != input_data.member_user_id:
            await self._check_editor_permission(user, group, input_data.group_id)
            await self._check_not_owner(group, input_data.member_user_id)

        return await self.group_member_repository.delete_membership(input_data.member_user_id, input_data.group_id)
