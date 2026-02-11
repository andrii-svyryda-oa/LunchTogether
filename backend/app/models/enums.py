import enum


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


# Role preset definitions mapping role -> scope values
GROUP_ROLE_PRESETS: dict[GroupRole, dict[str, str]] = {
    GroupRole.ADMIN: {
        "members_scope": MembersScope.EDITOR,
        "orders_scope": OrdersScope.EDITOR,
        "balances_scope": BalancesScope.EDITOR,
        "analytics_scope": AnalyticsScope.VIEWER,
        "restaurants_scope": RestaurantsScope.EDITOR,
    },
    GroupRole.SUPERVISOR_MEMBER: {
        "members_scope": MembersScope.VIEWER,
        "orders_scope": OrdersScope.INITIATOR,
        "balances_scope": BalancesScope.VIEWER,
        "analytics_scope": AnalyticsScope.VIEWER,
        "restaurants_scope": RestaurantsScope.VIEWER,
    },
    GroupRole.MEMBER: {
        "members_scope": MembersScope.NONE,
        "orders_scope": OrdersScope.PARTICIPANT,
        "balances_scope": BalancesScope.NONE,
        "analytics_scope": AnalyticsScope.NONE,
        "restaurants_scope": RestaurantsScope.VIEWER,
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
