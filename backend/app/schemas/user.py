import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class UserUpdate(BaseSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None


class UserResponse(BaseSchema):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    hashed_password: str
