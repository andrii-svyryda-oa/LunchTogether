import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.user import User
from app.repositories.group import GroupMemberRepository, GroupRepository
from app.schemas.group import GroupDetailResponse, GroupMemberResponse, PermissionResponse


class GetGroupDetailInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class GetGroupDetailOutput(BaseModel):
    group: GroupDetailResponse


class GetGroupDetailWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: GetGroupDetailInput) -> GetGroupDetailOutput:
        group = await self.group_repository.get_with_members(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        members = [
            GroupMemberResponse(
                id=m.id,
                user_id=m.user_id,
                group_id=m.group_id,
                permissions=[
                    PermissionResponse(permission_type=p.permission_type, level=p.level) for p in m.permissions
                ],
                created_at=m.created_at,
                updated_at=m.updated_at,
                user_full_name=m.user.full_name if m.user else None,
                user_email=m.user.email if m.user else None,
            )
            for m in group.members
        ]

        group_response = GroupDetailResponse(
            **{k: getattr(group, k) for k in GroupDetailResponse.model_fields if hasattr(group, k) and k != "members"},
            members=members,
        )
        return GetGroupDetailOutput(group=group_response)
