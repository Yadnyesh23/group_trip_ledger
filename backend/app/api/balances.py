from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_db
from app.models.users import UserModel
from app.services.balance import BalanceService

router = APIRouter(
    prefix="/trips/{trip_id}/balances",
    tags=["Balances"],
)


@router.get("/")
async def list_balances(
    trip_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db=Depends(get_db),
):
    service = BalanceService(db)

    balances = await service.get_balance_of_trip(
        trip_id=trip_id,
        current_user_id=current_user.id,
    )

    return {"balances": balances}
