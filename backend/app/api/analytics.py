import uuid

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_current_user,
    get_group_analytics_workflow,
    get_user_analytics_workflow,
)
from app.models.user import User
from app.schemas.analytics import GroupAnalyticsResponse, UserAnalyticsResponse
from app.workflows.analytics.group import GetGroupAnalyticsInput, GetGroupAnalyticsWorkflow
from app.workflows.analytics.user import GetUserAnalyticsInput, GetUserAnalyticsWorkflow

router = APIRouter(tags=["analytics"])


@router.get("/groups/{group_id}/analytics", response_model=GroupAnalyticsResponse)
async def get_group_analytics(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workflow: GetGroupAnalyticsWorkflow = Depends(get_group_analytics_workflow),
) -> GroupAnalyticsResponse:
    result = await workflow.execute(GetGroupAnalyticsInput(group_id=group_id, current_user=current_user))
    return result.analytics


@router.get("/users/me/analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    workflow: GetUserAnalyticsWorkflow = Depends(get_user_analytics_workflow),
) -> UserAnalyticsResponse:
    result = await workflow.execute(GetUserAnalyticsInput(current_user=current_user))
    return result.analytics
