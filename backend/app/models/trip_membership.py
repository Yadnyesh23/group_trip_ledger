
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    String,
    Date,
    DateTime,
    UUID,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class TripMembershipModel(Base):
    __tablename__ = "trip_members"

    __table_args__ = (
        UniqueConstraint(
            "trip_id",
            "user_id",
            name="uq_trip_member",
        ),
    )

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

    # NULL means this participant has no registered account.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Used for guests; registered members can use UserModel.name.
    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    joined_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )

    left_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
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

    @property
    def is_guest(self) -> bool:
        return self.user_id is None

    @property
    def guest_name(self) -> str | None:
        return self.display_name

    # Relationships
    trip = relationship(
        "TripModel",
        back_populates="trip_memberships",
    )

    user = relationship(
        "UserModel",
        back_populates="user_memberships",
    )

    expenses_paid = relationship(
        "ExpenseModel",
        back_populates="paid_by_member",
    )

    expense_participants = relationship(
        "ExpenseParticipantModel",
        back_populates="trip_member",
    )

    expense_allocations = relationship(
        "ExpenseAllocationModel",
        back_populates="trip_member",
    )

    payments_sent = relationship(
        "PaymentModel",
        foreign_keys="PaymentModel.from_member_id",
        back_populates="from_member",
    )

    payments_received = relationship(
        "PaymentModel",
        foreign_keys="PaymentModel.to_member_id",
        back_populates="to_member",
    )