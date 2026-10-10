
import uuid
from decimal import Decimal

from sqlalchemy import (
    UUID,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class ExpenseAllocationModel(Base):
    __tablename__ = "expense_allocations"

    __table_args__ = (
        UniqueConstraint(
            "expense_id",
            "trip_member_id",
            name="uq_expense_allocation",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("expenses.id"),
        nullable=False,
    )

    trip_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip_members.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Relationships
    expense = relationship(
        "ExpenseModel",
        back_populates="expense_allocations",
    )

    trip_member = relationship(
        "TripMembershipModel",
        back_populates="expense_allocations",
    )