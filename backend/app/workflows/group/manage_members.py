import uuid

from pydantic import BaseModel

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.enums import GROUP_ROLE_PRESETS, MembersScope
from app.models.group import Group
from app.models.user import User
from app.repositories.group import GroupMemberRepository, GroupRepository
from app.repositories.user import UserRepository
from app.schemas.group import GroupMemberCreate, GroupMemberResponse, GroupMemberUpdate


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


class ManageMembersWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        user_repository: UserRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.user_repository = user_repository

    async def _check_editor_permission(self, user: User, group: Group, group_id: uuid.UUID) -> None:
        """Check that the current user has Members Editor permission."""
        if user.is_admin:
            return

        membership = await self.group_member_repository.get_membership(user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
        if membership.members_scope != MembersScope.EDITOR:
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

        # Build permission data from role preset + optional overrides
        role_presets = GROUP_ROLE_PRESETS[input_data.data.role]
        member_data = {
            "user_id": input_data.data.user_id,
            "group_id": input_data.group_id,
            **role_presets,
        }

        # Apply optional scope overrides
        for scope_field in ["members_scope", "orders_scope", "balances_scope", "analytics_scope", "restaurants_scope"]:
            override = getattr(input_data.data, scope_field, None)
            if override is not None:
                member_data[scope_field] = override

        member = await self.group_member_repository.create(member_data)

        return AddMemberOutput(
            member=GroupMemberResponse(
                **{k: getattr(member, k) for k in GroupMemberResponse.model_fields if hasattr(member, k)},
                user_full_name=target_user.full_name,
                user_email=target_user.email,
            )
        )

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

        # Build update data
        update_data = {}

        # If role preset is provided, apply all presets first
        if input_data.data.role is not None:
            role_presets = GROUP_ROLE_PRESETS[input_data.data.role]
            update_data.update(role_presets)

        # Apply individual scope overrides
        for scope_field in ["members_scope", "orders_scope", "balances_scope", "analytics_scope", "restaurants_scope"]:
            override = getattr(input_data.data, scope_field, None)
            if override is not None:
                update_data[scope_field] = override

        if update_data:
            member = await self.group_member_repository.update(membership.id, update_data)
        else:
            member = membership

        target_user = await self.user_repository.get_by_id(input_data.member_user_id)

        return UpdateMemberOutput(
            member=GroupMemberResponse(
                **{k: getattr(member, k) for k in GroupMemberResponse.model_fields if hasattr(member, k)},
                user_full_name=target_user.full_name if target_user else None,
                user_email=target_user.email if target_user else None,
            )
        )

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
