import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class PermissionType(str, enum.Enum):
    MEMBERS = "members"
    ORDERS = "orders"
    BALANCES = "balances"
    ANALYTICS = "analytics"
    RESTAURANTS = "restaurants"


class MembersScope(str, enum.Enum):
    EDITOR = "editor"
    VIEWER = "viewer"
    NONE = "none"


class OrdersScope(str, enum.Enum):
    EDITOR = "editor"
    INITIATOR = "initiator"
    PARTICIPANT = "participant"


class BalancesScope(str, enum.Enum):
    EDITOR = "editor"
    VIEWER = "viewer"
    NONE = "none"


class AnalyticsScope(str, enum.Enum):
    VIEWER = "viewer"
    NONE = "none"


class RestaurantsScope(str, enum.Enum):
    EDITOR = "editor"
    VIEWER = "viewer"


class GroupRole(str, enum.Enum):
    """Predefined role presets that set all scopes at once."""

    ADMIN = "admin"
    SUPERVISOR_MEMBER = "supervisor_member"
    MEMBER = "member"


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


class OrderStatus(str, enum.Enum):
    INITIATED = "initiated"
    CONFIRMED = "confirmed"
    ORDERED = "ordered"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class BalanceChangeType(str, enum.Enum):
    MANUAL = "manual"
    ORDER = "order"
