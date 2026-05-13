from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email import EmailService
from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.repositories.analytics import GroupAnalyticsRepository, UserAnalyticsRepository
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
from app.workflows.analytics.group import GetGroupAnalyticsWorkflow
from app.workflows.analytics.user import GetUserAnalyticsWorkflow
from app.workflows.balance.adjust import AdjustBalanceWorkflow
from app.workflows.balance.get_history import GetBalanceHistoryWorkflow
from app.workflows.balance.get_my import GetMyBalanceWorkflow
from app.workflows.balance.list import ListBalancesWorkflow
from app.workflows.dish.create import CreateDishWorkflow
from app.workflows.dish.delete import DeleteDishWorkflow
from app.workflows.dish.list import ListDishesWorkflow
from app.workflows.dish.update import UpdateDishWorkflow
from app.workflows.favorite.list import ListFavoritesWorkflow
from app.workflows.favorite.toggle import ToggleFavoriteWorkflow
from app.workflows.group.add_member import AddMemberWorkflow
from app.workflows.group.create import CreateGroupWorkflow
from app.workflows.group.delete import DeleteGroupWorkflow
from app.workflows.group.get_detail import GetGroupDetailWorkflow
from app.workflows.group.list import ListGroupsWorkflow
from app.workflows.group.list_members import ListMembersWorkflow
from app.workflows.group.remove_member import RemoveMemberWorkflow
from app.workflows.group.update import UpdateGroupWorkflow
from app.workflows.group.update_member import UpdateMemberWorkflow
from app.workflows.group.upload_logo import UploadGroupLogoWorkflow
from app.workflows.invitation.accept import AcceptInvitationWorkflow
from app.workflows.invitation.cancel import CancelInvitationWorkflow
from app.workflows.invitation.create import CreateInvitationWorkflow
from app.workflows.invitation.decline import DeclineInvitationWorkflow
from app.workflows.invitation.link_to_user import LinkInvitationsToUserWorkflow
from app.workflows.invitation.list_my_pending import ListMyPendingWorkflow
from app.workflows.invitation.list_pending_for_group import ListPendingForGroupWorkflow
from app.workflows.invitation.preview_by_token import PreviewByTokenWorkflow
from app.workflows.order.create import CreateOrderWorkflow
from app.workflows.order.get_active import GetActiveOrderWorkflow
from app.workflows.order.get_detail import GetOrderDetailWorkflow
from app.workflows.order.list import ListOrdersWorkflow
from app.workflows.order.set_delivery_fee import SetDeliveryFeeWorkflow
from app.workflows.order.transition import TransitionOrderWorkflow
from app.workflows.order_item.add import AddOrderItemWorkflow
from app.workflows.order_item.delete import DeleteOrderItemWorkflow
from app.workflows.order_item.list import ListOrderItemsWorkflow
from app.workflows.order_item.update import UpdateOrderItemWorkflow
from app.workflows.permission.set_member_permissions import SetMemberPermissionsWorkflow
from app.workflows.restaurant.create import CreateRestaurantWorkflow
from app.workflows.restaurant.delete import DeleteRestaurantWorkflow
from app.workflows.restaurant.get import GetRestaurantWorkflow
from app.workflows.restaurant.list import ListRestaurantsWorkflow
from app.workflows.restaurant.update import UpdateRestaurantWorkflow
from app.workflows.user.admin_update import AdminUpdateUserWorkflow
from app.workflows.user.create import CreateUserWorkflow
from app.workflows.user.get import GetUserWorkflow
from app.workflows.user.list import ListUsersWorkflow
from app.workflows.user.login import LoginWorkflow
from app.workflows.user.register import RegisterWorkflow
from app.workflows.user.update import UpdateUserWorkflow

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


# --- Service factories ---


def get_email_service() -> EmailService:
    return EmailService()


# --- Workflow factories ---


def get_register_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
) -> RegisterWorkflow:
    return RegisterWorkflow(user_repository, invitation_repository)


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


def get_list_groups_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
) -> ListGroupsWorkflow:
    return ListGroupsWorkflow(group_repository)


def get_get_group_detail_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GetGroupDetailWorkflow:
    return GetGroupDetailWorkflow(group_repository, group_member_repository)


def get_update_group_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> UpdateGroupWorkflow:
    return UpdateGroupWorkflow(group_repository, group_member_repository)


def get_upload_group_logo_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> UploadGroupLogoWorkflow:
    return UploadGroupLogoWorkflow(group_repository, group_member_repository)


def get_delete_group_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
) -> DeleteGroupWorkflow:
    return DeleteGroupWorkflow(group_repository)


def get_list_members_workflow(
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> ListMembersWorkflow:
    return ListMembersWorkflow(group_member_repository)


def get_add_member_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> AddMemberWorkflow:
    return AddMemberWorkflow(group_repository, group_member_repository, user_repository, permission_repository)


def get_update_member_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> UpdateMemberWorkflow:
    return UpdateMemberWorkflow(group_repository, group_member_repository, user_repository, permission_repository)


def get_remove_member_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> RemoveMemberWorkflow:
    return RemoveMemberWorkflow(group_repository, group_member_repository)


def get_list_users_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> ListUsersWorkflow:
    return ListUsersWorkflow(user_repository)


def get_create_user_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> CreateUserWorkflow:
    return CreateUserWorkflow(user_repository)


def get_get_user_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUserWorkflow:
    return GetUserWorkflow(user_repository)


def get_update_user_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UpdateUserWorkflow:
    return UpdateUserWorkflow(user_repository)


def get_admin_update_user_workflow(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AdminUpdateUserWorkflow:
    return AdminUpdateUserWorkflow(user_repository)


def get_create_invitation_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> CreateInvitationWorkflow:
    return CreateInvitationWorkflow(
        group_repository, group_member_repository, invitation_repository, user_repository, email_service
    )


def get_accept_invitation_workflow(
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> AcceptInvitationWorkflow:
    return AcceptInvitationWorkflow(invitation_repository, group_member_repository, permission_repository)


def get_decline_invitation_workflow(
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
) -> DeclineInvitationWorkflow:
    return DeclineInvitationWorkflow(invitation_repository)


def get_cancel_invitation_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
) -> CancelInvitationWorkflow:
    return CancelInvitationWorkflow(group_repository, group_member_repository, invitation_repository)


def get_preview_by_token_workflow(
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> PreviewByTokenWorkflow:
    return PreviewByTokenWorkflow(invitation_repository, user_repository)


def get_list_my_pending_workflow(
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
) -> ListMyPendingWorkflow:
    return ListMyPendingWorkflow(invitation_repository)


def get_list_pending_for_group_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
) -> ListPendingForGroupWorkflow:
    return ListPendingForGroupWorkflow(group_repository, group_member_repository, invitation_repository)


def get_link_invitations_to_user_workflow(
    invitation_repository: GroupInvitationRepository = Depends(get_group_invitation_repository),
) -> LinkInvitationsToUserWorkflow:
    return LinkInvitationsToUserWorkflow(invitation_repository)


def get_create_order_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> CreateOrderWorkflow:
    return CreateOrderWorkflow(group_repository, group_member_repository, order_repository, restaurant_repository)


def get_list_orders_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> ListOrdersWorkflow:
    return ListOrdersWorkflow(order_repository, group_member_repository)


def get_get_order_detail_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
) -> GetOrderDetailWorkflow:
    return GetOrderDetailWorkflow(order_repository)


def get_get_active_order_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    get_detail_workflow: GetOrderDetailWorkflow = Depends(get_get_order_detail_workflow),
) -> GetActiveOrderWorkflow:
    return GetActiveOrderWorkflow(order_repository, group_member_repository, get_detail_workflow)


def get_transition_order_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    balance_history_repository: BalanceHistoryRepository = Depends(get_balance_history_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> TransitionOrderWorkflow:
    return TransitionOrderWorkflow(
        order_repository,
        order_item_repository,
        group_member_repository,
        balance_repository,
        balance_history_repository,
        dish_repository,
    )


def get_set_delivery_fee_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> SetDeliveryFeeWorkflow:
    return SetDeliveryFeeWorkflow(order_repository, order_item_repository, group_member_repository)


def get_list_order_items_workflow(
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> ListOrderItemsWorkflow:
    return ListOrderItemsWorkflow(order_item_repository, group_member_repository)


def get_add_order_item_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    dish_repository: DishRepository = Depends(get_dish_repository),
) -> AddOrderItemWorkflow:
    return AddOrderItemWorkflow(
        order_repository, order_item_repository, group_member_repository, user_repository, dish_repository
    )


def get_update_order_item_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> UpdateOrderItemWorkflow:
    return UpdateOrderItemWorkflow(order_repository, order_item_repository, group_member_repository)


def get_delete_order_item_workflow(
    order_repository: OrderRepository = Depends(get_order_repository),
    order_item_repository: OrderItemRepository = Depends(get_order_item_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> DeleteOrderItemWorkflow:
    return DeleteOrderItemWorkflow(order_repository, order_item_repository, group_member_repository)


def get_list_favorites_workflow(
    favorite_dish_repository: FavoriteDishRepository = Depends(get_favorite_dish_repository),
) -> ListFavoritesWorkflow:
    return ListFavoritesWorkflow(favorite_dish_repository)


def get_toggle_favorite_workflow(
    favorite_dish_repository: FavoriteDishRepository = Depends(get_favorite_dish_repository),
) -> ToggleFavoriteWorkflow:
    return ToggleFavoriteWorkflow(favorite_dish_repository)


def get_adjust_balance_workflow(
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    balance_history_repository: BalanceHistoryRepository = Depends(get_balance_history_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> AdjustBalanceWorkflow:
    return AdjustBalanceWorkflow(balance_repository, balance_history_repository, group_member_repository)


def get_list_balances_workflow(
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> ListBalancesWorkflow:
    return ListBalancesWorkflow(balance_repository, group_member_repository)


def get_my_balance_workflow(
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GetMyBalanceWorkflow:
    return GetMyBalanceWorkflow(balance_repository, group_member_repository)


def get_balance_history_workflow(
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    balance_history_repository: BalanceHistoryRepository = Depends(get_balance_history_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GetBalanceHistoryWorkflow:
    return GetBalanceHistoryWorkflow(balance_repository, balance_history_repository, group_member_repository)


def get_set_member_permissions_workflow(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
    permission_repository: GroupMemberPermissionRepository = Depends(get_group_member_permission_repository),
) -> SetMemberPermissionsWorkflow:
    return SetMemberPermissionsWorkflow(group_repository, group_member_repository, permission_repository)


def get_group_analytics_workflow(
    session: AsyncSession = Depends(get_db),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GetGroupAnalyticsWorkflow:
    return GetGroupAnalyticsWorkflow(GroupAnalyticsRepository(session), group_member_repository)


def get_user_analytics_workflow(
    session: AsyncSession = Depends(get_db),
) -> GetUserAnalyticsWorkflow:
    return GetUserAnalyticsWorkflow(UserAnalyticsRepository(session))


def get_list_restaurants_workflow(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> ListRestaurantsWorkflow:
    return ListRestaurantsWorkflow(restaurant_repository, group_member_repository)


def get_create_restaurant_workflow(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> CreateRestaurantWorkflow:
    return CreateRestaurantWorkflow(restaurant_repository, group_member_repository)


def get_get_restaurant_workflow(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> GetRestaurantWorkflow:
    return GetRestaurantWorkflow(restaurant_repository, group_member_repository)


def get_update_restaurant_workflow(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> UpdateRestaurantWorkflow:
    return UpdateRestaurantWorkflow(restaurant_repository, group_member_repository)


def get_delete_restaurant_workflow(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> DeleteRestaurantWorkflow:
    return DeleteRestaurantWorkflow(restaurant_repository, group_member_repository)


def get_list_dishes_workflow(
    dish_repository: DishRepository = Depends(get_dish_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> ListDishesWorkflow:
    return ListDishesWorkflow(dish_repository, group_member_repository)


def get_create_dish_workflow(
    dish_repository: DishRepository = Depends(get_dish_repository),
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> CreateDishWorkflow:
    return CreateDishWorkflow(dish_repository, restaurant_repository, group_member_repository)


def get_update_dish_workflow(
    dish_repository: DishRepository = Depends(get_dish_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> UpdateDishWorkflow:
    return UpdateDishWorkflow(dish_repository, group_member_repository)


def get_delete_dish_workflow(
    dish_repository: DishRepository = Depends(get_dish_repository),
    group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
) -> DeleteDishWorkflow:
    return DeleteDishWorkflow(dish_repository, group_member_repository)


# --- Auth dependencies ---


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    if access_token is None:
        raise AuthError(detail="Not authenticated")

    token_payload = decode_access_token(access_token)
    if token_payload is None:
        raise AuthError(detail="Invalid or expired token")

    user = await user_repository.get_by_id(token_payload.sub)
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
