import uuid
from datetime import datetime

from pydantic import Field

from app.models.enums import GroupRole, PermissionType
from app.schemas.base import BaseSchema

# --- Group ---


class GroupCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class GroupUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class GroupResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    logo_path: str | None
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    member_count: int | None = None


class GroupDetailResponse(GroupResponse):
    members: list["GroupMemberResponse"] = []


# --- Permission ---


class PermissionResponse(BaseSchema):
    permission_type: str
    level: str


class PermissionInput(BaseSchema):
    permission_type: PermissionType
    level: str


# --- Group Member ---


class GroupMemberCreate(BaseSchema):
    user_id: uuid.UUID
    role: GroupRole = GroupRole.MEMBER
    # Optional permission overrides after role preset
    permissions: list[PermissionInput] | None = None


class GroupMemberUpdate(BaseSchema):
    role: GroupRole | None = None
    # Optional permission overrides after role preset
    permissions: list[PermissionInput] | None = None


class GroupMemberResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    group_id: uuid.UUID
    permissions: list[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime
    user_full_name: str | None = None
    user_email: str | None = None


# --- Invitation ---


class InvitationCreate(BaseSchema):
    email: str = Field(max_length=255)
    role: GroupRole = GroupRole.MEMBER


class InvitationResponse(BaseSchema):
    id: uuid.UUID
    group_id: uuid.UUID
    inviter_id: uuid.UUID
    invitee_email: str
    invitee_id: uuid.UUID | None
    status: str
    token: str
    created_at: datetime
    updated_at: datetime
    inviter_full_name: str | None = None
    inviter_email: str | None = None


class InvitationAcceptResponse(BaseSchema):
    message: str
    group_id: uuid.UUID


class InvitationPreviewResponse(BaseSchema):
    """Public preview of an invitation — no auth required to fetch this."""

    group_id: uuid.UUID
    group_name: str
    group_logo_path: str | None
    inviter_full_name: str
    inviter_email: str
    invitee_email: str
    invitee_has_account: bool


class MyInvitationResponse(BaseSchema):
    """A pending invitation shown in the current user's own inbox."""

    id: uuid.UUID
    group_id: uuid.UUID
    group_name: str
    group_logo_path: str | None
    inviter_full_name: str | None
    invitee_email: str
    status: str
    token: str
    created_at: datetime
