from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expenses import ExpenseModel


class ExpenseRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        expense: ExpenseModel,
    ) -> ExpenseModel:

        self.db.add(expense)

        await self.db.flush()
        await self.db.refresh(expense)

        return expense

    async def get_expense_by_id(
        self,
        trip_id: UUID,
        expense_id: UUID,
    ) -> ExpenseModel | None:

        stmt = select(ExpenseModel).where(
            ExpenseModel.id == expense_id,
            ExpenseModel.trip_id == trip_id,
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all_expenses_of_trip(
        self,
        trip_id: UUID,
    ) -> list[ExpenseModel]:

        stmt = (
            select(ExpenseModel)
            .where(
                ExpenseModel.trip_id == trip_id
            )
            .order_by(
                ExpenseModel.expense_date.desc()
            )
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def update(
        self,
        expense: ExpenseModel,
        data: dict,
    ) -> ExpenseModel:

        for key, value in data.items():
            setattr(expense, key, value)

        await self.db.flush()

        return expense

    async def delete(
        self,
        expense: ExpenseModel,
    ) -> None:

        await self.db.delete(expense)

        await self.db.flush()