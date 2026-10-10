
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    String,
    Date,
    DateTime,
    UUID,
    ForeignKey,
    Numeric,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class SplitType(str, Enum):
    EQUAL = "EQUAL"
    CUSTOM = "CUSTOM"


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    split_type: Mapped[SplitType] = mapped_column(
        SQLAlchemyEnum(
            SplitType,
            name="expense_split_type",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # The payer is a trip member, not necessarily a registered user.
    paid_by_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip_members.id"),
        nullable=False,
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    trip = relationship(
        "TripModel",
        back_populates="expenses",
    )

    paid_by_member = relationship(
        "TripMembershipModel",
        back_populates="expenses_paid",
        foreign_keys=[paid_by_member_id],
    )

    expense_participants = relationship(
        "ExpenseParticipantModel",
        back_populates="expense",
    )

    expense_allocations = relationship(
        "ExpenseAllocationModel",
        back_populates="expense",
    )