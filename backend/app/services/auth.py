from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_tokens import RefreshTokenModel
from app.models.users import UserModel
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.users import UserRepository


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)

    async def register_user(
        self,
        name: str,
        email: EmailStr,
        password: str,
    ) -> UserModel:

        
        user_exists = await self.user_repo.get_by_email(email)

        if user_exists:
            raise ValueError("User already exists")

        
        hashed_password = hash_password(password)

        
        new_user = UserModel(
            name=name,
            email=email,
            hashed_password=hashed_password,
        )

        
        await self.user_repo.create(new_user)

        return new_user

    async def login_user(
        self,
        email: EmailStr,
        password: str,
    ) -> dict:

        
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ValueError("Invalid email or password")

        
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        
        refresh_token_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        
        refresh_token_model = RefreshTokenModel(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_token_expires_at,
        )

        
        await self.refresh_token_repo.create(refresh_token_model)

        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout_user(self, user_id: UUID) -> dict:

        await self.refresh_token_repo.revoke_all_for_user(user_id)

        return {
            "message": "User logged out successfully"
        }