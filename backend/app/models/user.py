from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import UserRole


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.USER,
        nullable=False,
    )
    navigate_to_active_order: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    # Relationships
    owned_groups: Mapped[list["Group"]] = relationship(  # noqa: F821
        "Group",
        back_populates="owner",
        foreign_keys="Group.owner_id",
    )
    group_memberships: Mapped[list["GroupMember"]] = relationship(  # noqa: F821
        "GroupMember",
        back_populates="user",
        foreign_keys="GroupMember.user_id",
    )
