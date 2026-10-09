from app.api import trip_membership
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

    async def get_settlements(
    self,
    current_user_id: UUID,
    trip_id: UUID,
):
    # 1. Make sure the trip exists
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
            status_code=404,
            detail="Trip not found",
        )

        if not await self.trip_repo.is_member(trip_id, current_user_id):
            raise HTTPException(
            status_code=403,
            detail="You are not a member of this trip",
        )

    # 2. Get trip balances, including user names
        balances = await self.balance_service.get_balance_of_trip(
            trip_id,
            current_user_id,
        )

    # 3. Build a mapping from user ID to name
        user_names = {
            balance["user_id"]: balance["user_name"]
            for balance in balances
        }

    # 4. Calculate settlements using the existing engine
        settlements = SettlementEngine.settle_balances(balances)

    # 5. Add names to the settlement results
        return [
            {
            **settlement,
            "payer_name": user_names.get(
                settlement["payer"], "Unknown user"
            ),
            "payee_name": user_names.get(
                settlement["payee"], "Unknown user"
            ),
        }
        for settlement in settlements
    ]