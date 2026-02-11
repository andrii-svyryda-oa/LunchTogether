import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class AdminUserCreate(BaseSchema):
    """Admin can create users with additional fields."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    is_admin: bool = False


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class UserUpdate(BaseSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    navigate_to_active_order: bool | None = None


class AdminUserUpdate(BaseSchema):
    """Admin can update additional user fields."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    navigate_to_active_order: bool | None = None


class UserResponse(BaseSchema):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    navigate_to_active_order: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    hashed_password: str
