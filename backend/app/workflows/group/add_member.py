import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.permissions import GROUP_ROLE_PRESETS
from app.models.enums import MembersScope, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberPermissionRepository, GroupMemberRepository, GroupRepository
from app.repositories.user import UserRepository
from app.schemas.group import GroupMemberCreate, GroupMemberResponse, PermissionResponse
from app.schemas.internal import GroupMemberInternalCreate


def _build_member_response(member, target_user=None) -> GroupMemberResponse:
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


class AddMemberInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    data: GroupMemberCreate
    current_user: User


class AddMemberOutput(BaseModel):
    member: GroupMemberResponse


class AddMemberWorkflow:
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

    async def execute(self, input_data: AddMemberInput) -> AddMemberOutput:
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

        member_count = await self.group_member_repository.count_members(input_data.group_id)
        if member_count >= 25:
            raise ValidationError(detail="Group has reached the maximum of 25 members")

        target_user = await self.user_repository.get_by_id(input_data.data.user_id)
        if target_user is None:
            raise NotFoundError(detail="User not found")

        existing = await self.group_member_repository.get_membership(input_data.data.user_id, input_data.group_id)
        if existing is not None:
            raise ConflictError(detail="User is already a member of this group")

        member = await self.group_member_repository.create(
            GroupMemberInternalCreate(user_id=input_data.data.user_id, group_id=input_data.group_id)
        )

        role_presets = GROUP_ROLE_PRESETS[input_data.data.role]
        permissions_data = {pt.value: level for pt, level in role_presets.items()}

        if input_data.data.permissions:
            for perm in input_data.data.permissions:
                permissions_data[perm.permission_type.value] = perm.level

        await self.permission_repository.set_permissions(member.id, permissions_data)

        member = await self.group_member_repository.get_membership(input_data.data.user_id, input_data.group_id)
        return AddMemberOutput(member=_build_member_response(member, target_user))
