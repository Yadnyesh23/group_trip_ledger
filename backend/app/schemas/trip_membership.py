import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

# =========================
# REQUESTS
# =========================
class AddMemberRequest(BaseModel):
    user_id : uuid.UUID


# =========================
# RESPONSES
# =========================
class TripMemberResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: date
    left_at: date | None
    status: str
    created_at: datetime
    updated_at: datetime

    # model_config = ConfigDict(from_attributes=True)

class AddTripMemberResponse(BaseModel):
    status_code: int
    message: str
    data: TripMemberResponse

class TripMemberListResponse(BaseModel):
    members: list[TripMemberResponse]