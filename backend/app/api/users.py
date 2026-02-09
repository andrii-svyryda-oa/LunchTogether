import uuid

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import ForbiddenError, NotFoundError
from app.dependencies import get_current_user, get_user_repository
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.base import PaginatedResponse
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_user_repository),
) -> PaginatedResponse[UserResponse]:
    result = await user_repository.get_multi(page=page, page_size=page_size)
    result.items = [UserResponse.model_validate(user) for user in result.items]
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise NotFoundError(detail="User not found")
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    # Users can only update their own profile
    if current_user.id != user_id:
        raise ForbiddenError(detail="You can only update your own profile")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return UserResponse.model_validate(current_user)

    user = await user_repository.update(user_id, update_data)
    if user is None:
        raise NotFoundError(detail="User not found")
    return UserResponse.model_validate(user)
