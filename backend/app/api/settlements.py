from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_db
from app.models.users import UserModel
from app.services.settlement import SettlementService

router = APIRouter(
    prefix="/trips/{trip_id}/settlements",
    tags=["Settlements"],
)


@router.get("/")
async def get_settlements(trip_id : UUID, current_user : UserModel = Depends(get_current_user), db=Depends(get_db)):
    service = SettlementService(db)
    settlements = await service.get_settlements(current_user.id, trip_id)
    return {"settlements": settlements}