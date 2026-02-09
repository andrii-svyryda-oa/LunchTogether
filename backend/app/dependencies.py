import uuid

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.workflows.user.login import LoginWorkflow
from app.workflows.user.register import RegisterWorkflow


# --- Repository factories ---


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


# --- Workflow factories ---


def get_register_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> RegisterWorkflow:
    return RegisterWorkflow(user_repository)


def get_login_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> LoginWorkflow:
    return LoginWorkflow(user_repository)


# --- Auth dependencies ---


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    if access_token is None:
        raise AuthError(detail="Not authenticated")

    subject = decode_access_token(access_token)
    if subject is None:
        raise AuthError(detail="Invalid or expired token")

    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise AuthError(detail="Invalid token payload")

    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise AuthError(detail="User not found")

    if not user.is_active:
        raise AuthError(detail="User account is deactivated")

    return user
