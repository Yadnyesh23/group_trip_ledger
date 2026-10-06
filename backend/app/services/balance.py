from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException

from app.repositories.expenses import ExpenseRepository
from app.repositories.expense_allocations import ExpenseAllocationRepository
from app.repositories.trips import TripRepository
from app.services.balance_engine import BalanceEngine

class BalanceService:
    def __init__(self, db: AsyncSession):
        self.expense_repo = ExpenseRepository(db)
        self.allocation_repo = ExpenseAllocationRepository(db)
        self.trip_repo = TripRepository(db)

    async def get_balance_of_trip(self, trip_id: UUID, current_user_id: UUID) -> list[dict]:
        trip = await self.trip_repo.get_trip_by_id(trip_id)
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        if not await self.trip_repo.is_member(trip_id, current_user_id):
            raise HTTPException(status_code=403, detail="You are not a member of this trip")

        expenses = await self.expense_repo.get_all_expenses_of_trip(trip_id)
        allocations = await self.allocation_repo.get_all_allocations_by_trip(trip_id)

        balances = BalanceEngine.calculate_balances(
            [
                {"id": e.id, "name": e.name, "amount": e.amount,
                 "paid_by_user_id": e.paid_by_user_id}
                for e in expenses
            ],
            [
                {"expense_id": a.expense_id, "user_id": a.user_id, "amount": a.amount}
                for a in allocations
            ],
        )
        return [{"user_id": uid, "balance": bal} for uid, bal in balances.items()]