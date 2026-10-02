import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, UUID, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class TripMembershipModel(Base):
    __tablename__ = "trip_members"

    __table_args__ = (
        UniqueConstraint(
            "trip_id",
            "user_id",
            name="uq_trip_member"
        ),
    )

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

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    joined_at: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    left_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE"
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

    trip = relationship(
        "TripModel",
        back_populates="trip_memberships"
    )

    user = relationship(
        "UserModel",
        back_populates="user_memberships"
    )