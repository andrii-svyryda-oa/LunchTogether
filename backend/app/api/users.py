import uuid

from fastapi import APIRouter, Depends, Query

from app.dependencies import (
    get_admin_update_user_workflow,
    get_create_user_workflow,
    get_current_admin,
    get_current_user,
    get_get_user_workflow,
    get_list_users_workflow,
    get_update_user_workflow,
)
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserResponse, UserUpdate
from app.workflows.user.admin_update import AdminUpdateUserInput, AdminUpdateUserWorkflow
from app.workflows.user.create import CreateUserInput, CreateUserWorkflow
from app.workflows.user.get import GetUserInput, GetUserWorkflow
from app.workflows.user.list import ListUsersInput, ListUsersWorkflow
from app.workflows.user.update import UpdateUserInput, UpdateUserWorkflow

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    workflow: ListUsersWorkflow = Depends(get_list_users_workflow),
) -> PaginatedResponse[UserResponse]:
    result = await workflow.execute(ListUsersInput(page=page, page_size=page_size, current_user=current_user))
    return result.result


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    data: AdminUserCreate,
    _current_user: User = Depends(get_current_admin),
    workflow: CreateUserWorkflow = Depends(get_create_user_workflow),
) -> UserResponse:
    result = await workflow.execute(CreateUserInput(data=data))
    return result.user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    workflow: GetUserWorkflow = Depends(get_get_user_workflow),
) -> UserResponse:
    result = await workflow.execute(GetUserInput(user_id=user_id))
    return result.user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    workflow: UpdateUserWorkflow = Depends(get_update_user_workflow),
) -> UserResponse:
    result = await workflow.execute(UpdateUserInput(user_id=user_id, data=data, current_user=current_user))
    return result.user


@router.put("/{user_id}/admin", response_model=UserResponse)
async def admin_update_user(
    user_id: uuid.UUID,
    data: AdminUserUpdate,
    _current_user: User = Depends(get_current_admin),
    workflow: AdminUpdateUserWorkflow = Depends(get_admin_update_user_workflow),
) -> UserResponse:
    result = await workflow.execute(AdminUpdateUserInput(user_id=user_id, data=data))
    return result.user
