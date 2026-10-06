from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException

from app.repositories.trips import TripRepository
from app.services.balance import BalanceService
from app.services.settlement_engine import SettlementEngine

class SettlementService:

    def __init__(self, db : AsyncSession):
        self.db = db
        self.balance_service = BalanceService(db)
        self.trip_repo = TripRepository(db)

    async def get_settlements(self, current_user_id : UUID, trip_id : UUID):
        # 1. Make sure trip exists
        trip = await self.trip_repo.get_trip_by_id(trip_id)
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        if not await self.trip_repo.is_member(trip_id, current_user_id):
            raise HTTPException(status_code=403, detail="You are not a member of this trip")

        # 2. Get current trip balances
        balances = await self.balance_service.get_balance_of_trip(trip_id, current_user_id)

        # 3. Give balances to SettlementEngine
        settlements = SettlementEngine.settle_balances(balances)

        # 4. Return the settlement suggestions
        return settlements