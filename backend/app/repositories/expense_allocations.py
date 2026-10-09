from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense_allocations import ExpenseAllocationModel
from app.models.expenses import ExpenseModel
from app.models.users import UserModel


class ExpenseAllocationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        allocation: ExpenseAllocationModel,
    ) -> ExpenseAllocationModel:
        self.db.add(allocation)
        await self.db.flush()
        await self.db.refresh(allocation)
        return allocation

    async def get_all_allocations_by_trip(
        self,
        trip_id: UUID,
    ) -> list[ExpenseAllocationModel]:
        stmt = (
            select(ExpenseAllocationModel)
            .join(
                ExpenseModel,
                ExpenseAllocationModel.expense_id == ExpenseModel.id,
            )
            .where(ExpenseModel.trip_id == trip_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_allocations_with_names_by_trip(
        self,
        trip_id: UUID,
    ) -> list[tuple[ExpenseAllocationModel, str]]:
        stmt = (
            select(ExpenseAllocationModel, UserModel.name)
            .join(
                ExpenseModel,
                ExpenseAllocationModel.expense_id == ExpenseModel.id,
            )
            .join(
                UserModel,
                ExpenseAllocationModel.user_id == UserModel.id,
            )
            .where(ExpenseModel.trip_id == trip_id)
        )

        result = await self.db.execute(stmt)
        return list(result.all())