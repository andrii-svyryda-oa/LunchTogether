import uuid

from fastapi import APIRouter, Depends, UploadFile

from app.core.exceptions import NotFoundError
from app.dependencies import (
    get_accept_invitation_workflow,
    get_add_member_workflow,
    get_cancel_invitation_workflow,
    get_create_group_workflow,
    get_create_invitation_workflow,
    get_current_user,
    get_decline_invitation_workflow,
    get_delete_group_workflow,
    get_get_group_detail_workflow,
    get_list_groups_workflow,
    get_list_members_workflow,
    get_list_my_pending_workflow,
    get_list_pending_for_group_workflow,
    get_preview_by_token_workflow,
    get_remove_member_workflow,
    get_update_group_workflow,
    get_update_member_workflow,
    get_upload_group_logo_workflow,
)
from app.models.user import User
from app.schemas.base import MessageResponse
from app.schemas.group import (
    GroupCreate,
    GroupDetailResponse,
    GroupMemberCreate,
    GroupMemberResponse,
    GroupMemberUpdate,
    GroupResponse,
    GroupUpdate,
    InvitationAcceptResponse,
    InvitationCreate,
    InvitationPreviewResponse,
    InvitationResponse,
    MyInvitationResponse,
)
from app.workflows.group.add_member import AddMemberInput, AddMemberWorkflow
from app.workflows.group.create import CreateGroupInput, CreateGroupWorkflow
from app.workflows.group.delete import DeleteGroupInput, DeleteGroupWorkflow
from app.workflows.group.get_detail import GetGroupDetailInput, GetGroupDetailWorkflow
from app.workflows.group.list import ListGroupsInput, ListGroupsWorkflow
from app.workflows.group.list_members import ListMembersInput, ListMembersWorkflow
from app.workflows.group.remove_member import RemoveMemberInput, RemoveMemberWorkflow
from app.workflows.group.update import UpdateGroupInput, UpdateGroupWorkflow
from app.workflows.group.update_member import UpdateMemberInput, UpdateMemberWorkflow
from app.workflows.group.upload_logo import UploadGroupLogoInput, UploadGroupLogoWorkflow
from app.workflows.invitation.accept import AcceptInvitationInput, AcceptInvitationWorkflow
from app.workflows.invitation.cancel import CancelInvitationInput, CancelInvitationWorkflow
from app.workflows.invitation.create import CreateInvitationInput, CreateInvitationWorkflow
from app.workflows.invitation.decline import DeclineInvitationInput, DeclineInvitationWorkflow
from app.workflows.invitation.list_my_pending import ListMyPendingInput, ListMyPendingWorkflow
from app.workflows.invitation.list_pending_for_group import ListPendingForGroupInput, ListPendingForGroupWorkflow
from app.workflows.invitation.preview_by_token import PreviewByTokenInput, PreviewByTokenWorkflow

router = APIRouter(prefix="/groups", tags=["groups"])


# --- Group CRUD ---


@router.get("", response_model=list[GroupResponse])
async def list_groups(
    current_user: User = Depends(get_current_user),
    workflow: ListGroupsWorkflow = Depends(get_list_groups_workflow),
) -> list[GroupResponse]:
    result = await workflow.execute(ListGroupsInput(current_user=current_user))
    return result.groups


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
    workflow: GetGroupDetailWorkflow = Depends(get_get_group_detail_workflow),
) -> GroupDetailResponse:
    result = await workflow.execute(GetGroupDetailInput(group_id=group_id, current_user=current_user))
    return result.group


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: uuid.UUID,
    data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    workflow: UpdateGroupWorkflow = Depends(get_update_group_workflow),
) -> GroupResponse:
    result = await workflow.execute(UpdateGroupInput(group_id=group_id, data=data, current_user=current_user))
    return result.group


@router.post("/{group_id}/logo", response_model=GroupResponse)
async def upload_group_logo(
    group_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    workflow: UploadGroupLogoWorkflow = Depends(get_upload_group_logo_workflow),
) -> GroupResponse:
    result = await workflow.execute(UploadGroupLogoInput(group_id=group_id, file=file, current_user=current_user))
    return result.group


@router.delete("/{group_id}", response_model=MessageResponse)
async def delete_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: DeleteGroupWorkflow = Depends(get_delete_group_workflow),
) -> MessageResponse:
    await workflow.execute(DeleteGroupInput(group_id=group_id, current_user=current_user))
    return MessageResponse(message="Group deleted successfully")


# --- Members ---


@router.get("/{group_id}/members", response_model=list[GroupMemberResponse])
async def list_members(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListMembersWorkflow = Depends(get_list_members_workflow),
) -> list[GroupMemberResponse]:
    result = await workflow.execute(ListMembersInput(group_id=group_id, current_user=current_user))
    return result.members


@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=201)
async def add_member(
    group_id: uuid.UUID,
    data: GroupMemberCreate,
    current_user: User = Depends(get_current_user),
    workflow: AddMemberWorkflow = Depends(get_add_member_workflow),
) -> GroupMemberResponse:
    result = await workflow.execute(AddMemberInput(group_id=group_id, data=data, current_user=current_user))
    return result.member


@router.patch("/{group_id}/members/{member_user_id}", response_model=GroupMemberResponse)
async def update_member(
    group_id: uuid.UUID,
    member_user_id: uuid.UUID,
    data: GroupMemberUpdate,
    current_user: User = Depends(get_current_user),
    workflow: UpdateMemberWorkflow = Depends(get_update_member_workflow),
) -> GroupMemberResponse:
    result = await workflow.execute(
        UpdateMemberInput(group_id=group_id, member_user_id=member_user_id, data=data, current_user=current_user)
    )
    return result.member


@router.delete("/{group_id}/members/{member_user_id}", response_model=MessageResponse)
async def remove_member(
    group_id: uuid.UUID,
    member_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: RemoveMemberWorkflow = Depends(get_remove_member_workflow),
) -> MessageResponse:
    result = await workflow.execute(
        RemoveMemberInput(group_id=group_id, member_user_id=member_user_id, current_user=current_user)
    )
    if not result.removed:
        raise NotFoundError(detail="Member not found")
    return MessageResponse(message="Member removed successfully")


# --- Invitations ---


@router.get("/{group_id}/invitations", response_model=list[InvitationResponse])
async def list_pending_invitations(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListPendingForGroupWorkflow = Depends(get_list_pending_for_group_workflow),
) -> list[InvitationResponse]:
    result = await workflow.execute(ListPendingForGroupInput(group_id=group_id, current_user=current_user))
    return result.invitations


@router.post("/{group_id}/invitations", response_model=InvitationResponse, status_code=201)
async def create_invitation(
    group_id: uuid.UUID,
    data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    workflow: CreateInvitationWorkflow = Depends(get_create_invitation_workflow),
) -> InvitationResponse:
    result = await workflow.execute(CreateInvitationInput(group_id=group_id, data=data, current_user=current_user))
    return result.invitation


@router.delete("/{group_id}/invitations/{invitation_id}", response_model=MessageResponse)
async def cancel_invitation(
    group_id: uuid.UUID,
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: CancelInvitationWorkflow = Depends(get_cancel_invitation_workflow),
) -> MessageResponse:
    await workflow.execute(
        CancelInvitationInput(group_id=group_id, invitation_id=invitation_id, current_user=current_user)
    )
    return MessageResponse(message="Invitation cancelled")


@router.get("/invitations/by-token/{token}", response_model=InvitationPreviewResponse)
async def preview_invitation(
    token: str,
    workflow: PreviewByTokenWorkflow = Depends(get_preview_by_token_workflow),
) -> InvitationPreviewResponse:
    result = await workflow.execute(PreviewByTokenInput(token=token))
    return result.preview


@router.get("/invitations/mine", response_model=list[MyInvitationResponse])
async def my_pending_invitations(
    current_user: User = Depends(get_current_user),
    workflow: ListMyPendingWorkflow = Depends(get_list_my_pending_workflow),
) -> list[MyInvitationResponse]:
    result = await workflow.execute(ListMyPendingInput(current_user=current_user))
    return result.invitations


@router.post("/invitations/{token}/accept", response_model=InvitationAcceptResponse)
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    workflow: AcceptInvitationWorkflow = Depends(get_accept_invitation_workflow),
) -> InvitationAcceptResponse:
    result = await workflow.execute(AcceptInvitationInput(token=token, current_user=current_user))
    return result.result


@router.post("/invitations/{token}/decline", response_model=MessageResponse)
async def decline_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    workflow: DeclineInvitationWorkflow = Depends(get_decline_invitation_workflow),
) -> MessageResponse:
    await workflow.execute(DeclineInvitationInput(token=token, current_user=current_user))
    return MessageResponse(message="Invitation declined")
