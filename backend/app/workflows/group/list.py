from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.repositories.group import GroupRepository
from app.schemas.group import GroupResponse


class ListGroupsInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    current_user: User


class ListGroupsOutput(BaseModel):
    groups: list[GroupResponse]


class ListGroupsWorkflow:
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository

    async def execute(self, input_data: ListGroupsInput) -> ListGroupsOutput:
        user = input_data.current_user
        if user.is_admin:
            result = await self.group_repository.get_multi(page=1, page_size=1000)
            groups = [GroupResponse.model_validate(g) for g in result.items]
        else:
            raw = await self.group_repository.get_groups_for_user(user.id)
            groups = [GroupResponse.model_validate(g) for g in raw]
        return ListGroupsOutput(groups=groups)
