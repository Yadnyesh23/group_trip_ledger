
import uuid

from sqlalchemy import UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class ExpenseParticipantModel(Base):
    __tablename__ = "expense_participants"

    __table_args__ = (
        UniqueConstraint(
            "expense_id",
            "trip_member_id",
            name="uq_expense_participant",
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

    # Relationships
    expense = relationship(
        "ExpenseModel",
        back_populates="expense_participants",
    )

    trip_member = relationship(
        "TripMembershipModel",
        back_populates="expense_participants",
    )