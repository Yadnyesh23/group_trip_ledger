
import uuid
from decimal import Decimal
from datetime import datetime, date, timezone

from sqlalchemy import (
    UUID,
    ForeignKey,
    Date,
    Numeric,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class PaymentModel(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_payment_amount_positive",
        ),
        CheckConstraint(
            "from_member_id != to_member_id",
            name="ck_payment_different_members",
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

    # The person who actually sent the money.
    from_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip_members.id"),
        nullable=False,
    )

    # The person who actually received the money.
    to_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip_members.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    payment_date: Mapped[date] = mapped_column(
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
        back_populates="payments",
    )

    from_member = relationship(
        "TripMembershipModel",
        foreign_keys=[from_member_id],
        back_populates="payments_sent",
    )

    to_member = relationship(
        "TripMembershipModel",
        foreign_keys=[to_member_id],
        back_populates="payments_received",
    )