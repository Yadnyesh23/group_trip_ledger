import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import datetime, date, timezone
from sqlalchemy import(
    UUID, 
    ForeignKey,
    Date,
    Numeric,
    DateTime
)
from app.database.db import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id"),
        nullable=False
    )

    from_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    to_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    trip = relationship(
        "TripModel",
        back_populates="payments"
    )

    from_user = relationship(
        "UserModel",
        foreign_keys=[from_user_id],
        back_populates="payments_sent"
    )

    to_user = relationship(
        "UserModel",
        foreign_keys=[to_user_id],
        back_populates="payments_received"
    )