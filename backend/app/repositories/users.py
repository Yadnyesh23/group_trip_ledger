from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserModel


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def delete(self, user: UserModel) -> None:
        await self.db.delete(user)
        await self.db.commit()