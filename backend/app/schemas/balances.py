from pydantic import BaseModel
import uuid
from decimal import Decimal


class TripBalanceResponse(BaseModel):
    member_id: uuid.UUID
    member_name: str
    balance: Decimal


class TripBalanceListResponse(BaseModel):
    balances: list[TripBalanceResponse]