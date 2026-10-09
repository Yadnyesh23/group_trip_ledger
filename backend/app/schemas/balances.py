from pydantic import BaseModel
import uuid
from decimal import Decimal

class TripBalanceResponse(BaseModel):
    user_id : uuid.UUID
    user_name: str
    balance : Decimal

class TripBalanceListResponse(BaseModel):
    balances : list[TripBalanceResponse]