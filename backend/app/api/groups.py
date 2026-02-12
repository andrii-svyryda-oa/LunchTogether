import uuid

from fastapi import APIRouter, Depends, UploadFile

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.storage import save_upload
from app.dependencies import (
    get_create_group_workflow,
    get_current_user,
    get_group_member_repository,
    get_group_repository,
    get_invite_workflow,
    get_manage_members_workflow,
)
from app.models.enums import MembersScope, PermissionType
from app.models.user import User
from app.repositories.group import GroupMemberRepository, GroupRepository
from app.schemas.base import MessageResponse
from app.schemas.group import (
    GroupCreate,
    GroupDetailResponse,
    GroupMemberCreate,
    GroupMemberResponse,
    GroupMemberUpdate,
    GroupResponse,
    GroupUpdate,
    InvitationCreate,
    InvitationResponse,
    PermissionResponse,
)
from app.workflows.group.create import CreateGroupInput, CreateGroupWorkflow
from app.workflows.group.invite import AcceptInviteInput, InviteInput, InviteWorkflow
from app.workflows.group.manage_members import (
    AddMemberInput,
    ManageMembersWorkflow,
    RemoveMemberInput,
    UpdateMemberInput,
)

router = APIRouter(prefix="/groups", tags=["groups"])


# --- Group CRUD ---


@router.get("", response_model=list[GroupResponse])
async def list_groups(
    current_user: User = Depends(get_current_user),
    group_repository: GroupRepository = Depends(get_group_repository),
) -> list[GroupResponse]:
    """List groups for the current user (admins see all)."""
    if current_user.is_admin:
        result = await group_repository.get_multi(page=1, page_size=1000)
        return [GroupResponse.model_validate(g) for g in result.items]
    else:
        groups = await group_repository.get_groups_for_user(current_user.id)
        return [GroupResponse.model_validate(g) for g in groups]


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(
    data: GroupCreate,
    current_user: User = Depends(get_current_user),
    workflow: CreateGroupWorkflow = Depends(get_create_group_workflow),
) -> GroupResponse:
    result = await workflow.execute(CreateGroupInput(data=data, current_user=current_user))
    return result.group


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GroupDetailResponse:
    group = await group_repository.get_with_members(group_id)
    if group is None:
        raise NotFoundError(detail="Group not found")

    # Check access
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")

    members = [
        GroupMemberResponse(
            id=m.id,
            user_id=m.user_id,
            group_id=m.group_id,
            permissions=[PermissionResponse(permission_type=p.permission_type, level=p.level) for p in m.permissions],
            created_at=m.created_at,
            updated_at=m.updated_at,
            user_full_name=m.user.full_name if m.user else None,
            user_email=m.user.email if m.user else None,
        )
        for m in group.members
    ]

    return GroupDetailResponse(
        **{k: getattr(group, k) for k in GroupResponse.model_fields if hasattr(group, k)},
        members=members,
    )


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: uuid.UUID,
    data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GroupResponse:
    group = await group_repository.get_by_id(group_id)
    if group is None:
        raise NotFoundError(detail="Group not found")

    # Only owner, members editors, or admins can update
    if not current_user.is_admin and group.owner_id != current_user.id:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None or membership.get_permission(PermissionType.MEMBERS) != MembersScope.EDITOR:
            raise ForbiddenError(detail="You do not have permission to update this group")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return GroupResponse.model_validate(group)

    updated = await group_repository.update(group_id, update_data)
    return GroupResponse.model_validate(updated)


@router.post("/{group_id}/logo", response_model=GroupResponse)
async def upload_group_logo(
    group_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GroupResponse:
    group = await group_repository.get_by_id(group_id)
    if group is None:
        raise NotFoundError(detail="Group not found")

    if not current_user.is_admin and group.owner_id != current_user.id:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None or membership.get_permission(PermissionType.MEMBERS) != MembersScope.EDITOR:
            raise ForbiddenError(detail="You do not have permission to update this group")

    file_path = await save_upload(file, subdirectory="group-logos")
    updated = await group_repository.update(group_id, {"logo_path": file_path})
    return GroupResponse.model_validate(updated)


@router.delete("/{group_id}", response_model=MessageResponse)
async def delete_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_repository: GroupRepository = Depends(get_group_repository),
) -> MessageResponse:
    group = await group_repository.get_by_id(group_id)
    if group is None:
        raise NotFoundError(detail="Group not found")

    if not current_user.is_admin and group.owner_id != current_user.id:
        raise ForbiddenError(detail="Only the group owner or an admin can delete this group")

    await group_repository.delete(group_id)
    return MessageResponse(message="Group deleted successfully")


# --- Members ---


@router.get("/{group_id}/members", response_model=list[GroupMemberResponse])
async def list_members(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> list[GroupMemberResponse]:
    # Check access
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")

    members = await group_member_repository.get_members_for_group(group_id)
    return [
        GroupMemberResponse(
            id=m.id,
            user_id=m.user_id,
            group_id=m.group_id,
            permissions=[PermissionResponse(permission_type=p.permission_type, level=p.level) for p in m.permissions],
            created_at=m.created_at,
            updated_at=m.updated_at,
            user_full_name=m.user.full_name if m.user else None,
            user_email=m.user.email if m.user else None,
        )
        for m in members
    ]


@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=201)
async def add_member(
    group_id: uuid.UUID,
    data: GroupMemberCreate,
    current_user: User = Depends(get_current_user),
    workflow: ManageMembersWorkflow = Depends(get_manage_members_workflow),
) -> GroupMemberResponse:
    result = await workflow.add_member(AddMemberInput(group_id=group_id, data=data, current_user=current_user))
    return result.member


@router.patch("/{group_id}/members/{member_user_id}", response_model=GroupMemberResponse)
async def update_member(
    group_id: uuid.UUID,
    member_user_id: uuid.UUID,
    data: GroupMemberUpdate,
    current_user: User = Depends(get_current_user),
    workflow: ManageMembersWorkflow = Depends(get_manage_members_workflow),
) -> GroupMemberResponse:
    result = await workflow.update_member(
        UpdateMemberInput(group_id=group_id, member_user_id=member_user_id, data=data, current_user=current_user)
    )
    return result.member


@router.delete("/{group_id}/members/{member_user_id}", response_model=MessageResponse)
async def remove_member(
    group_id: uuid.UUID,
    member_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ManageMembersWorkflow = Depends(get_manage_members_workflow),
) -> MessageResponse:
    removed = await workflow.remove_member(
        RemoveMemberInput(group_id=group_id, member_user_id=member_user_id, current_user=current_user)
    )
    if not removed:
        raise NotFoundError(detail="Member not found")
    return MessageResponse(message="Member removed successfully")


# --- Invitations ---


@router.post("/{group_id}/invitations", response_model=InvitationResponse, status_code=201)
async def create_invitation(
    group_id: uuid.UUID,
    data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    workflow: InviteWorkflow = Depends(get_invite_workflow),
) -> InvitationResponse:
    result = await workflow.create_invitation(InviteInput(group_id=group_id, data=data, current_user=current_user))
    return result.invitation


@router.post("/invitations/{token}/accept", response_model=MessageResponse)
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    workflow: InviteWorkflow = Depends(get_invite_workflow),
) -> MessageResponse:
    result = await workflow.accept_invitation(AcceptInviteInput(token=token, current_user=current_user))
    return MessageResponse(message=result.result.message)


@router.post("/invitations/{token}/decline", response_model=MessageResponse)
async def decline_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    workflow: InviteWorkflow = Depends(get_invite_workflow),
) -> MessageResponse:
    await workflow.decline_invitation(token, current_user)
    return MessageResponse(message="Invitation declined")
