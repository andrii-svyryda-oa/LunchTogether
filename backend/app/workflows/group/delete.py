import uuid

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.user import User
from app.repositories.group import GroupRepository


class DeleteGroupInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class DeleteGroupOutput(BaseModel):
    deleted: bool


class DeleteGroupWorkflow:
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository

    async def execute(self, input_data: DeleteGroupInput) -> DeleteGroupOutput:
        group = await self.group_repository.get_by_id(input_data.group_id)
        if group is None:
            raise NotFoundError(detail="Group not found")

        if not input_data.current_user.is_admin and group.owner_id != input_data.current_user.id:
            raise ForbiddenError(detail="Only the group owner or an admin can delete this group")

        deleted = await self.group_repository.delete(input_data.group_id)
        return DeleteGroupOutput(deleted=deleted)
