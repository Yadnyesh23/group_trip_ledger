from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.expenses import SplitType


# =========================
# REQUESTS
# =========================

class ExpenseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    description: str | None = Field(
        default=None,
        max_length=500
    )

    amount: Decimal = Field(gt=0)

    split_type: SplitType

    category: str | None = Field(
        default=None,
        max_length=100
    )

    paid_by_user_id: UUID

    participant_user_ids: list[UUID] = Field(
        min_length=1
    )

    custom_allocation: dict[UUID, Decimal] | None = None

    expense_date: date


class ExpenseUpdateRequest(BaseModel):
    pass


# =========================
# RESPONSES
# =========================

class ExpenseAllocationResponse(BaseModel):
    user_id: UUID
    amount: Decimal

    model_config = {
        "from_attributes": True
    }


class ExpenseResponse(BaseModel):
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

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ExpenseListResponse(BaseModel):
    total_expenses : int
    expenses : list[ExpenseResponse]