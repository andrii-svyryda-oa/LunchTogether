import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Restaurant(BaseModel):
    __tablename__ = "restaurants"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    group: Mapped["Group"] = relationship(  # noqa: F821
        "Group",
        back_populates="restaurants",
    )
    dishes: Mapped[list["Dish"]] = relationship(
        "Dish",
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )


class Dish(BaseModel):
    __tablename__ = "dishes"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    detail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="dishes",
    )
