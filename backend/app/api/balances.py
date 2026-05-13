import uuid

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_adjust_balance_workflow,
    get_balance_history_workflow,
    get_current_user,
    get_list_balances_workflow,
    get_my_balance_workflow,
)
from app.models.user import User
from app.schemas.balance import BalanceAdjustmentCreate, BalanceHistoryResponse, BalanceResponse
from app.workflows.balance.adjust import AdjustBalanceInput, AdjustBalanceWorkflow
from app.workflows.balance.get_history import GetBalanceHistoryInput, GetBalanceHistoryWorkflow
from app.workflows.balance.get_my import GetMyBalanceInput, GetMyBalanceWorkflow
from app.workflows.balance.list import ListBalancesInput, ListBalancesWorkflow

router = APIRouter(prefix="/groups/{group_id}/balances", tags=["balances"])


@router.get("", response_model=list[BalanceResponse])
async def list_balances(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: ListBalancesWorkflow = Depends(get_list_balances_workflow),
) -> list[BalanceResponse]:
    result = await workflow.execute(ListBalancesInput(group_id=group_id, current_user=current_user))
    return result.balances


@router.get("/me", response_model=BalanceResponse)
async def get_my_balance(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: GetMyBalanceWorkflow = Depends(get_my_balance_workflow),
) -> BalanceResponse:
    result = await workflow.execute(GetMyBalanceInput(group_id=group_id, current_user=current_user))
    return result.balance


@router.post("/adjust", response_model=BalanceResponse)
async def adjust_balance(
    group_id: uuid.UUID,
    data: BalanceAdjustmentCreate,
    current_user: User = Depends(get_current_user),
    workflow: AdjustBalanceWorkflow = Depends(get_adjust_balance_workflow),
) -> BalanceResponse:
    result = await workflow.execute(AdjustBalanceInput(group_id=group_id, data=data, current_user=current_user))
    return result.balance


@router.get("/{user_id}/history", response_model=list[BalanceHistoryResponse])
async def get_balance_history(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: GetBalanceHistoryWorkflow = Depends(get_balance_history_workflow),
) -> list[BalanceHistoryResponse]:
    result = await workflow.execute(
        GetBalanceHistoryInput(group_id=group_id, user_id=user_id, current_user=current_user)
    )
    return result.history
