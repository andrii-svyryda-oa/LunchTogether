from app.models.enums import (
    AnalyticsScope,
    BalancesScope,
    GroupRole,
    MembersScope,
    OrdersScope,
    PermissionType,
    RestaurantsScope,
)

# Role preset definitions mapping role -> {permission_type: level}
GROUP_ROLE_PRESETS: dict[GroupRole, dict[PermissionType, str]] = {
    GroupRole.ADMIN: {
        PermissionType.MEMBERS: MembersScope.EDITOR,
        PermissionType.ORDERS: OrdersScope.EDITOR,
        PermissionType.BALANCES: BalancesScope.EDITOR,
        PermissionType.ANALYTICS: AnalyticsScope.VIEWER,
        PermissionType.RESTAURANTS: RestaurantsScope.EDITOR,
    },
    GroupRole.SUPERVISOR_MEMBER: {
        PermissionType.MEMBERS: MembersScope.VIEWER,
        PermissionType.ORDERS: OrdersScope.INITIATOR,
        PermissionType.BALANCES: BalancesScope.VIEWER,
        PermissionType.ANALYTICS: AnalyticsScope.VIEWER,
        PermissionType.RESTAURANTS: RestaurantsScope.VIEWER,
    },
    GroupRole.MEMBER: {
        PermissionType.MEMBERS: MembersScope.NONE,
        PermissionType.ORDERS: OrdersScope.PARTICIPANT,
        PermissionType.BALANCES: BalancesScope.NONE,
        PermissionType.ANALYTICS: AnalyticsScope.NONE,
        PermissionType.RESTAURANTS: RestaurantsScope.VIEWER,
    },
}
