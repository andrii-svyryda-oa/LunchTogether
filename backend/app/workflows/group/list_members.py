import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.schemas.group import GroupMemberResponse, PermissionResponse


class ListMembersInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class ListMembersOutput(BaseModel):
    members: list[GroupMemberResponse]


class ListMembersWorkflow:
    def __init__(self, group_member_repository: GroupMemberRepository):
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: ListMembersInput) -> ListMembersOutput:
        if not input_data.current_user.is_admin:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")

        members = await self.group_member_repository.get_members_for_group(input_data.group_id)
        return ListMembersOutput(
            members=[
                GroupMemberResponse(
                    id=m.id,
                    user_id=m.user_id,
                    group_id=m.group_id,
                    permissions=[
                        PermissionResponse(permission_type=p.permission_type, level=p.level)
                        for p in m.permissions
                    ],
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                    user_full_name=m.user.full_name if m.user else None,
                    user_email=m.user.email if m.user else None,
                )
                for m in members
            ]
        )
