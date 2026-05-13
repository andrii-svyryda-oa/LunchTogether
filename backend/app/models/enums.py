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
