import uuid

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import hash_password
from app.dependencies import get_current_admin, get_current_user, get_user_repository
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.base import PaginatedResponse
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_user_repository),
) -> PaginatedResponse[UserResponse]:
    # Only admins can list all users
    if not current_user.is_admin:
        raise ForbiddenError(detail="Admin access required to list all users")
    result = await user_repository.get_multi(page=page, page_size=page_size)
    result.items = [UserResponse.model_validate(user) for user in result.items]
    return result


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    data: AdminUserCreate,
    _current_user: User = Depends(get_current_admin),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Admin-only: create a new user."""
    if await user_repository.exists_by_email(data.email):
        raise ConflictError(detail="User with this email already exists")

    user = await user_repository.create(
        {
            "email": data.email,
            "hashed_password": hash_password(data.password),
            "full_name": data.full_name,
            "is_admin": data.is_admin,
        }
    )
    return UserResponse.model_validate(user)


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
    # Users can only update their own profile (admins can update anyone)
    if current_user.id != user_id and not current_user.is_admin:
        raise ForbiddenError(detail="You can only update your own profile")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        target = await user_repository.get_by_id(user_id)
        if target is None:
            raise NotFoundError(detail="User not found")
        return UserResponse.model_validate(target)

    user = await user_repository.update(user_id, update_data)
    if user is None:
        raise NotFoundError(detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/{user_id}/admin", response_model=UserResponse)
async def admin_update_user(
    user_id: uuid.UUID,
    data: AdminUserUpdate,
    _current_user: User = Depends(get_current_admin),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    """Admin-only: update any user's details including admin status."""
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        user = await user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(detail="User not found")
        return UserResponse.model_validate(user)

    user = await user_repository.update(user_id, update_data)
    if user is None:
        raise NotFoundError(detail="User not found")
    return UserResponse.model_validate(user)
