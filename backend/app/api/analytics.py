import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.database import get_db
from app.dependencies import get_current_user, get_group_member_repository
from app.models.balance import Balance
from app.models.enums import AnalyticsScope, OrderStatus, PermissionType
from app.models.group import GroupMember
from app.models.order import Order, OrderItem
from app.models.user import User
from app.repositories.group import GroupMemberRepository
from app.schemas.analytics import GroupAnalytics, UserAnalytics

router = APIRouter(tags=["analytics"])


@router.get("/groups/{group_id}/analytics", response_model=GroupAnalytics)
async def get_group_analytics(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    session: AsyncSession = Depends(get_db),
) -> GroupAnalytics:
    # Permission check
    if not current_user.is_admin:
        membership = await group_member_repository.get_membership(current_user.id, group_id)
        if membership is None:
            raise ForbiddenError(detail="You are not a member of this group")
        analytics_level = membership.get_permission(PermissionType.ANALYTICS)
        if analytics_level == AnalyticsScope.NONE or analytics_level is None:
            raise ForbiddenError(detail="You do not have permission to view analytics")

    # Total orders
    total_query = select(func.count()).select_from(Order).where(Order.group_id == group_id)
    total_orders = (await session.execute(total_query)).scalar_one()

    # Completed orders
    completed_query = (
        select(func.count()).select_from(Order).where(Order.group_id == group_id, Order.status == OrderStatus.FINISHED)
    )
    completed_orders = (await session.execute(completed_query)).scalar_one()

    # Cancelled
    cancelled_query = (
        select(func.count()).select_from(Order).where(Order.group_id == group_id, Order.status == OrderStatus.CANCELLED)
    )
    cancelled_orders = (await session.execute(cancelled_query)).scalar_one()

    # Active
    active_query = (
        select(func.count())
        .select_from(Order)
        .where(
            Order.group_id == group_id,
            Order.status.notin_([OrderStatus.FINISHED, OrderStatus.CANCELLED]),
        )
    )
    active_orders = (await session.execute(active_query)).scalar_one()

    # Members
    members_query = select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)
    total_members = (await session.execute(members_query)).scalar_one()

    # Total spent (sum of all order items in finished orders)
    spent_query = (
        select(func.coalesce(func.sum(OrderItem.price), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.group_id == group_id, Order.status == OrderStatus.FINISHED)
    )
    total_spent = (await session.execute(spent_query)).scalar_one()

    avg_value = Decimal(str(total_spent)) / Decimal(str(completed_orders)) if completed_orders > 0 else Decimal("0.00")

    # Most popular restaurant
    restaurant_query = (
        select(Order.restaurant_name, func.count().label("cnt"))
        .where(Order.group_id == group_id, Order.restaurant_name.isnot(None))
        .group_by(Order.restaurant_name)
        .order_by(func.count().desc())
        .limit(1)
    )
    restaurant_result = (await session.execute(restaurant_query)).first()
    most_popular = restaurant_result[0] if restaurant_result else None

    return GroupAnalytics(
        total_orders=total_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        active_orders=active_orders,
        total_members=total_members,
        total_spent=Decimal(str(total_spent)),
        average_order_value=avg_value.quantize(Decimal("0.01")),
        most_popular_restaurant=most_popular,
    )


@router.get("/users/me/analytics", response_model=UserAnalytics)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserAnalytics:
    # Total groups
    groups_query = select(func.count()).select_from(GroupMember).where(GroupMember.user_id == current_user.id)
    total_groups = (await session.execute(groups_query)).scalar_one()

    # Total orders participated in
    orders_query = select(func.count(func.distinct(OrderItem.order_id))).where(OrderItem.user_id == current_user.id)
    total_orders = (await session.execute(orders_query)).scalar_one()

    # Total spent
    spent_query = (
        select(func.coalesce(func.sum(OrderItem.price), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(OrderItem.user_id == current_user.id, Order.status == OrderStatus.FINISHED)
    )
    total_spent = (await session.execute(spent_query)).scalar_one()

    avg_value = Decimal(str(total_spent)) / Decimal(str(total_orders)) if total_orders > 0 else Decimal("0.00")

    # Favorite restaurant
    fav_query = (
        select(Order.restaurant_name, func.count().label("cnt"))
        .join(OrderItem, Order.id == OrderItem.order_id)
        .where(OrderItem.user_id == current_user.id, Order.restaurant_name.isnot(None))
        .group_by(Order.restaurant_name)
        .order_by(func.count().desc())
        .limit(1)
    )
    fav_result = (await session.execute(fav_query)).first()
    fav_restaurant = fav_result[0] if fav_result else None

    # Total balance across groups
    balance_query = select(func.coalesce(func.sum(Balance.amount), 0)).where(Balance.user_id == current_user.id)
    total_balance = (await session.execute(balance_query)).scalar_one()

    return UserAnalytics(
        total_groups=total_groups,
        total_orders_participated=total_orders,
        total_spent=Decimal(str(total_spent)),
        average_order_value=avg_value.quantize(Decimal("0.01")),
        favorite_restaurant=fav_restaurant,
        total_balance_across_groups=Decimal(str(total_balance)),
    )
