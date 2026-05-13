import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ForbiddenError
from app.models.enums import AnalyticsScope, PermissionType
from app.models.user import User
from app.repositories.analytics import GroupAnalyticsRepository
from app.repositories.group import GroupMemberRepository
from app.schemas.analytics import GroupAnalyticsResponse


class GetGroupAnalyticsInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    group_id: uuid.UUID
    current_user: User


class GetGroupAnalyticsOutput(BaseModel):
    analytics: GroupAnalyticsResponse


class GetGroupAnalyticsWorkflow:
    def __init__(
        self,
        analytics_repository: GroupAnalyticsRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.analytics_repository = analytics_repository
        self.group_member_repository = group_member_repository

    async def execute(self, input_data: GetGroupAnalyticsInput) -> GetGroupAnalyticsOutput:
        user = input_data.current_user
        if not user.is_admin:
            membership = await self.group_member_repository.get_membership(user.id, input_data.group_id)
            if membership is None:
                raise ForbiddenError(detail="You are not a member of this group")
            analytics_level = membership.get_permission(PermissionType.ANALYTICS)
            if analytics_level == AnalyticsScope.NONE or analytics_level is None:
                raise ForbiddenError(detail="You do not have permission to view analytics")

        repo = self.analytics_repository
        gid = input_data.group_id

        total_orders = await repo.count_orders(gid)
        completed_orders = await repo.count_completed_orders(gid)
        cancelled_orders = await repo.count_cancelled_orders(gid)
        active_orders = await repo.count_active_orders(gid)
        total_members = await repo.count_members(gid)
        total_spent = await repo.get_total_spent(gid)
        most_popular = await repo.get_most_popular_restaurant(gid)

        avg_value = total_spent / Decimal(str(completed_orders)) if completed_orders > 0 else Decimal("0.00")

        return GetGroupAnalyticsOutput(
            analytics=GroupAnalyticsResponse(
                total_orders=total_orders,
                completed_orders=completed_orders,
                cancelled_orders=cancelled_orders,
                active_orders=active_orders,
                total_members=total_members,
                total_spent=total_spent.quantize(Decimal("0.01")),
                average_order_value=avg_value.quantize(Decimal("0.01")),
                most_popular_restaurant=most_popular,
            )
        )
