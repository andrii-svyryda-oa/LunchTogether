import uuid

from fastapi import APIRouter, Depends

from app.core.exceptions import ForbiddenError, NotFoundError
from app.dependencies import (
    get_adjust_balance_workflow,
    get_balance_history_repository,
    get_balance_repository,
    get_current_user,
    get_group_member_repository,
)
from app.models.enums import BalancesScope, PermissionType
from app.models.user import User
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository
from app.repositories.group import GroupMemberRepository
from app.schemas.balance import BalanceAdjustment, BalanceHistoryResponse, BalanceResponse
from app.workflows.balance.adjust import AdjustBalanceInput, AdjustBalanceWorkflow

router = APIRouter(prefix="/groups/{group_id}/balances", tags=["balances"])


async def _check_balance_permission(
    user: User,
    group_id: uuid.UUID,
    group_member_repository: GroupMemberRepository,
    require_editor: bool = False,
) -> None:
    if user.is_admin:
        return
    membership = await group_member_repository.get_membership(user.id, group_id)
    if membership is None:
        raise ForbiddenError(detail="You are not a member of this group")
    balances_level = membership.get_permission(PermissionType.BALANCES)
    if balances_level == BalancesScope.NONE or balances_level is None:
        raise ForbiddenError(detail="You do not have permission to view balances")
    if require_editor and balances_level != BalancesScope.EDITOR:
        raise ForbiddenError(detail="You do not have permission to adjust balances")


@router.get("", response_model=list[BalanceResponse])
async def list_balances(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> list[BalanceResponse]:
    await _check_balance_permission(current_user, group_id, group_member_repository)
    balances = await balance_repository.get_balances_for_group(group_id)
    return [
        BalanceResponse(
            **{k: getattr(b, k) for k in BalanceResponse.model_fields if hasattr(b, k)},
            user_full_name=b.user.full_name if b.user else None,
        )
        for b in balances
    ]


@router.get("/me", response_model=BalanceResponse)
async def get_my_balance(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> BalanceResponse:
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")

    balance = await balance_repository.get_or_create(current_user.id, group_id)
    return BalanceResponse.model_validate(balance)


@router.post("/adjust", response_model=BalanceResponse)
async def adjust_balance(
    group_id: uuid.UUID,
    data: BalanceAdjustment,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    workflow: AdjustBalanceWorkflow = Depends(get_adjust_balance_workflow),
) -> BalanceResponse:
    await _check_balance_permission(current_user, group_id, group_member_repository, require_editor=True)
    result = await workflow.execute(AdjustBalanceInput(group_id=group_id, data=data, current_user=current_user))
    return result.balance


@router.get("/{user_id}/history", response_model=list[BalanceHistoryResponse])
async def get_balance_history(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    balance_history_repository: BalanceHistoryRepository = Depends(get_balance_history_repository),
) -> list[BalanceHistoryResponse]:
    await _check_balance_permission(current_user, group_id, group_member_repository)

    balance = await balance_repository.get_by_user_and_group(user_id, group_id)
    if balance is None:
        raise NotFoundError(detail="Balance not found")

    history = await balance_history_repository.get_history_for_balance(balance.id)
    return [
        BalanceHistoryResponse(
            **{k: getattr(h, k) for k in BalanceHistoryResponse.model_fields if hasattr(h, k)},
            created_by_name=h.created_by.full_name if h.created_by else None,
        )
        for h in history
    ]
