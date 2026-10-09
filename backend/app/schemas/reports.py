from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.expenses import SplitType
from app.schemas.trip_membership import TripMemberListResponse
from app.schemas.balances import TripBalanceListResponse
from app.schemas.settlements import SettlementListResponse


class ReportAllocationResponse(BaseModel):
    user_id: UUID
    user_name: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class ReportExpenseResponse(BaseModel):
    id: UUID
    trip_id: UUID
    name: str
    description: str | None
    amount: Decimal
    split_type: SplitType
    category: str | None
    paid_by_user_id: UUID
    paid_by_name: str
    expense_date: date

    allocations: list[ReportAllocationResponse]

    model_config = ConfigDict(from_attributes=True)


class ReportExpenseListResponse(BaseModel):
    total_expenses: int
    expenses: list[ReportExpenseResponse]


class ReportResponseSchema(BaseModel):
    members: TripMemberListResponse
    expenses: ReportExpenseListResponse
    balances: TripBalanceListResponse
    settlements: SettlementListResponse
