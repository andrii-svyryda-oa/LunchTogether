import uuid

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.repositories.balance import BalanceHistoryRepository, BalanceRepository
from app.repositories.group import (
    GroupInvitationRepository,
    GroupMemberPermissionRepository,
    GroupMemberRepository,
    GroupRepository,
)
from app.repositories.order import FavoriteDishRepository, OrderItemRepository, OrderRepository
from app.repositories.restaurant import DishRepository, RestaurantRepository
from app.repositories.user import UserRepository
from app.workflows.balance.adjust import AdjustBalanceWorkflow
from app.workflows.group.create import CreateGroupWorkflow
from app.workflows.group.invite import InviteWorkflow
from app.workflows.group.manage_members import ManageMembersWorkflow
from app.workflows.order.create import CreateOrderWorkflow
from app.workflows.order.lifecycle import OrderLifecycleWorkflow
from app.workflows.user.login import LoginWorkflow
from app.workflows.user.register import RegisterWorkflow

# --- Repository factories ---


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_group_repository(session: AsyncSession = Depends(get_db)) -> GroupRepository:
    return GroupRepository(session)


def get_group_member_repository(session: AsyncSession = Depends(get_db)) -> GroupMemberRepository:
    return GroupMemberRepository(session)


def get_group_member_permission_repository(session: AsyncSession = Depends(get_db)) -> GroupMemberPermissionRepository:
    return GroupMemberPermissionRepository(session)


def get_group_invitation_repository(session: AsyncSession = Depends(get_db)) -> GroupInvitationRepository:
    return GroupInvitationRepository(session)


def get_restaurant_repository(session: AsyncSession = Depends(get_db)) -> RestaurantRepository:
    return RestaurantRepository(session)


def get_dish_repository(session: AsyncSession = Depends(get_db)) -> DishRepository:
    return DishRepository(session)


def get_order_repository(session: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(session)


def get_order_item_repository(session: AsyncSession = Depends(get_db)) -> OrderItemRepository:
    return OrderItemRepository(session)


def get_favorite_dish_repository(session: AsyncSession = Depends(get_db)) -> FavoriteDishRepository:
    return FavoriteDishRepository(session)


def get_balance_repository(session: AsyncSession = Depends(get_db)) -> BalanceRepository:
    return BalanceRepository(session)


def get_balance_history_repository(session: AsyncSession = Depends(get_db)) -> BalanceHistoryRepository:
    return BalanceHistoryRepository(session)


# --- Workflow factories ---


def get_register_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> RegisterWorkflow:
    return RegisterWorkflow(user_repository)


def get_login_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> LoginWorkflow:
    return LoginWorkflow(user_repository)


def get_create_group_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> CreateGroupWorkflow:
    return CreateGroupWorkflow(group_repository, group_member_repository, permission_repository)


def get_manage_members_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> ManageMembersWorkflow:
    return ManageMembersWorkflow(group_repository, group_member_repository, user_repository, permission_repository)


def get_invite_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> InviteWorkflow:
    return InviteWorkflow(
        group_repository, group_member_repository, invitation_repository, user_repository, permission_repository
    )


def get_create_order_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> CreateOrderWorkflow:
    return CreateOrderWorkflow(group_repository, group_member_repository, order_repository, restaurant_repository)


def get_order_lifecycle_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    balance_history_repository: BalanceHistoryRepository = Depends(get_balance_history_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> OrderLifecycleWorkflow:
    return OrderLifecycleWorkflow(
        order_repository,
        order_item_repository,
        group_member_repository,
        balance_repository,
        balance_history_repository,
        dish_repository,
    )


def get_adjust_balance_workflow(
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    balance_history_repository: BalanceHistoryRepository = Depends(get_balance_history_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> AdjustBalanceWorkflow:
    return AdjustBalanceWorkflow(balance_repository, balance_history_repository, group_member_repository)


# --- Auth dependencies ---


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    if access_token is None:
        raise AuthError(detail="Not authenticated")

    subject = decode_access_token(access_token)
    if subject is None:
        raise AuthError(detail="Invalid or expired token")

    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise AuthError(detail="Invalid token payload")

    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise AuthError(detail="User not found")

    if not user.is_active:
        raise AuthError(detail="User account is deactivated")

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    from app.models.enums import UserRole

    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError(detail="Admin access required")
    return current_user
