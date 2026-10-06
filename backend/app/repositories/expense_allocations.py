from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense_allocations import ExpenseAllocationModel
from app.models.expenses import ExpenseModel


class ExpenseAllocationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, allocation: ExpenseAllocationModel) -> ExpenseAllocationModel:
        self.db.add(allocation)
        await self.db.flush()
        await self.db.refresh(allocation)
        return allocation

    async def get_all_allocations_by_trip(self, trip_id: UUID) -> list[ExpenseAllocationModel]:
        stmt = (
            select(ExpenseAllocationModel)
            .join(ExpenseModel, ExpenseAllocationModel.expense_id == ExpenseModel.id)
            .where(ExpenseModel.trip_id == trip_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())