import uuid

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.storage import save_upload
from app.models.enums import MembersScope, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository, GroupRepository
from app.schemas.group import GroupResponse
from app.schemas.internal import GroupLogoUpdate


class UploadGroupLogoInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    file: UploadFile
    current_user: User


class UploadGroupLogoOutput(BaseModel):
    group: GroupResponse


class UploadGroupLogoWorkflow:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: UploadGroupLogoInput) -> UploadGroupLogoOutput:
        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if not input_data.current_user.is_admin and group.owner_id != input_data.current_user.id:
            membership = await self.group_member_repository.get_membership(
                input_data.current_user.id, input_data.group_id
            )
            if membership is None or membership.get_permission(PermissionType.MEMBERS) != MembersScope.EDITOR:
                raise ForbiddenError(detail="You do not have permission to update this group")

        file_path = await save_upload(input_data.file, subdirectory="group-logos")
        updated = await self.group_repository.update(input_data.group_id, GroupLogoUpdate(logo_path=file_path))
        return UploadGroupLogoOutput(group=GroupResponse.model_validate(updated))
