from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_tokens import RefreshTokenModel


class RefreshTokenRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        token: RefreshTokenModel
    ) -> RefreshTokenModel:

        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)

        return token

    async def get_by_token(
        self,
        token: str
    ) -> RefreshTokenModel | None:

        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token == token
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def revoke(
        self,
        token: RefreshTokenModel
    ) -> None:

        token.revoked = True
        await self.db.commit()

    async def revoke_all_for_user(
        self,
        user_id: UUID
    ) -> None:

        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id
        )

        result = await self.db.execute(stmt)

        for token in result.scalars():
            token.revoked = True

        await self.db.commit()