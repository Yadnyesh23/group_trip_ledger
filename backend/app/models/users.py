from sqlalchemy.orm import mapped_collection, relationship
from sqlalchemy import String, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid 

from app.database.db import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
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
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    refresh_tokens = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )


