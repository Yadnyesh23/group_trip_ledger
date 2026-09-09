from sqlalchemy.orm import mapped_collection
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.database.db import Base

class UserModel(Base):
    __tablename__ = "users"

    id : Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False
    )

    name : Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email : Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )
    hashed_password : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    created_at : Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    # Yet to be written


