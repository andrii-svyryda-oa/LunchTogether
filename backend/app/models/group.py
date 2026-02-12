import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import InvitationStatus, PermissionType


class Group(BaseModel):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    logo_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    owner: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="owned_groups",
        foreign_keys=[owner_id],
    )
    members: Mapped[list["GroupMember"]] = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    invitations: Mapped[list["GroupInvitation"]] = relationship(
        "GroupInvitation",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    restaurants: Mapped[list["Restaurant"]] = relationship(  # noqa: F821
        "Restaurant",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["Order"]] = relationship(  # noqa: F821
        "Order",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    balances: Mapped[list["Balance"]] = relationship(  # noqa: F821
        "Balance",
        back_populates="group",
        cascade="all, delete-orphan",
    )


class GroupMember(BaseModel):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_group_member_user_group"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="group_memberships",
        foreign_keys=[user_id],
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="members",
        foreign_keys=[group_id],
    )
    permissions: Mapped[list["GroupMemberPermission"]] = relationship(
        "GroupMemberPermission",
        back_populates="group_member",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def get_permission(self, permission_type: str | PermissionType) -> str | None:
        """Get the level for a given permission type, or None if not set."""
        pt = permission_type.value if isinstance(permission_type, PermissionType) else permission_type
        for perm in self.permissions:
            if perm.permission_type == pt:
                return perm.level
        return None


class GroupMemberPermission(BaseModel):
    __tablename__ = "group_member_permissions"
    __table_args__ = (UniqueConstraint("group_member_id", "permission_type", name="uq_group_member_permission_type"),)

    group_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("group_members.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Relationships
    group_member: Mapped["GroupMember"] = relationship(
        "GroupMember",
        back_populates="permissions",
    )


class GroupInvitation(BaseModel):
    __tablename__ = "group_invitations"

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    inviter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    invitee_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    invitee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=InvitationStatus.PENDING,
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    # Relationships
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="invitations",
    )
    inviter: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[inviter_id],
    )
    invitee: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[invitee_id],
    )
