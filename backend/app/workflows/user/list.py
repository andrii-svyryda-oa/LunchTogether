from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.base import PaginatedResponse
from app.schemas.user import UserResponse


class ListUsersInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    page: int = 1
    page_size: int = 20
    current_user: User


class ListUsersOutput(BaseModel):
    result: PaginatedResponse


class ListUsersWorkflow:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, input_data: ListUsersInput) -> ListUsersOutput:
        if input_data.current_user.role != UserRole.ADMIN:
            raise ForbiddenError(detail="Admin access required to list all users")

        result = await self.user_repository.get_multi(page=input_data.page, page_size=input_data.page_size)
        result.items = [UserResponse.model_validate(u) for u in result.items]
        return ListUsersOutput(result=result)
