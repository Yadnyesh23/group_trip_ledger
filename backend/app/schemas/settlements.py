from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


class SettlementResponse(BaseModel):
    payer: UUID
    payer_name: str

    payee: UUID
    payee_name: str

    amount: Decimal


class SettlementListResponse(BaseModel):
    settlements: list[SettlementResponse]