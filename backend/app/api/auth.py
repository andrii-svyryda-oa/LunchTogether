from fastapi import APIRouter, Depends, Response

from app.dependencies import get_current_user, get_login_workflow, get_register_workflow
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.workflows.user.login import LoginInput, LoginWorkflow
from app.workflows.user.register import RegisterInput, RegisterWorkflow

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserCreate,
    workflow: RegisterWorkflow = Depends(get_register_workflow),
) -> UserResponse:
    result = await workflow.execute(RegisterInput(data=data))
    return result.user


@router.post("/login", response_model=UserResponse)
async def login(
    data: UserLogin,
    response: Response,
    workflow: LoginWorkflow = Depends(get_login_workflow),
) -> UserResponse:
    result = await workflow.execute(LoginInput(data=data))

    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 60,  # 30 minutes
    )

    return result.user


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
