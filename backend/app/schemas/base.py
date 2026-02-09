import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseResponseSchema(BaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseSchema, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseSchema):
    message: str
