from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

class SettlementResponse(BaseModel):
    payer: UUID
    payee: UUID
    amount: Decimal

class SettlementListResponse(BaseModel):
    settlements: list[SettlementResponse]