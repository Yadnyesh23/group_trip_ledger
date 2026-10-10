
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expenses import ExpenseModel
from app.models.trip_membership import TripMembershipModel
from app.models.users import UserModel


class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, expense: ExpenseModel) -> ExpenseModel:
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
            .where(ExpenseModel.trip_id == trip_id)
            .order_by(ExpenseModel.expense_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _expense_with_payer_name_query(self):
        payer_name = func.coalesce(
            UserModel.name,
            TripMembershipModel.display_name,
        ).label("payer_name")

        return (
            select(ExpenseModel, payer_name)
            .join(
                TripMembershipModel,
                ExpenseModel.paid_by_member_id == TripMembershipModel.id,
            )
            .outerjoin(
                UserModel,
                TripMembershipModel.user_id == UserModel.id,
            )
        )

    async def get_expense_with_payer_name(
        self,
        trip_id: UUID,
        expense_id: UUID,
    ) -> tuple[ExpenseModel, str] | None:
        stmt = self._expense_with_payer_name_query().where(
            ExpenseModel.id == expense_id,
            ExpenseModel.trip_id == trip_id,
        )

        result = await self.db.execute(stmt)
        return result.one_or_none()

    async def get_all_expenses_with_payer_names(
        self,
        trip_id: UUID,
    ) -> list[tuple[ExpenseModel, str]]:
        stmt = (
            self._expense_with_payer_name_query()
            .where(ExpenseModel.trip_id == trip_id)
            .order_by(ExpenseModel.expense_date.desc())
        )

        result = await self.db.execute(stmt)
        return list(result.all())

    async def update(
        self,
        expense: ExpenseModel,
        data: dict,
    ) -> ExpenseModel:
        for key, value in data.items():
            setattr(expense, key, value)

        await self.db.flush()
        return expense

    async def delete(self, expense: ExpenseModel) -> None:
        await self.db.delete(expense)
        await self.db.flush()