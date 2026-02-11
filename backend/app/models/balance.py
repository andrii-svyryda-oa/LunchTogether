import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import BalanceChangeType


class Balance(BaseModel):
    __tablename__ = "balances"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_balance_user_group"),)

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
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
    )
    group: Mapped["Group"] = relationship(  # noqa: F821
        "Group",
        back_populates="balances",
    )
    history: Mapped[list["BalanceHistory"]] = relationship(
        "BalanceHistory",
        back_populates="balance",
        cascade="all, delete-orphan",
    )


class BalanceHistory(BaseModel):
    __tablename__ = "balance_history"

    balance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("balances.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    change_type: Mapped[str] = mapped_column(
        String(20),
        default=BalanceChangeType.MANUAL,
        nullable=False,
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    balance: Mapped["Balance"] = relationship(
        "Balance",
        back_populates="history",
    )
    order: Mapped["Order | None"] = relationship(  # noqa: F821
        "Order",
    )
    created_by: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
    )
