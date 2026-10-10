from pydantic import BaseModel
import uuid
from decimal import Decimal


class AllocationResponse(BaseModel):
    expense_id: uuid.UUID
    member_id: uuid.UUID
    member_name: str
    amount: Decimal


class AllocationListResponse(BaseModel):
    allocations: list[AllocationResponse]
