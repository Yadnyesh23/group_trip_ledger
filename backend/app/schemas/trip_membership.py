import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AddMemberRequest(BaseModel):
    display_name: str = Field(
        min_length=1,
        max_length=100,
    )


class TripMemberResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    user_id: uuid.UUID | None
    user_name: str
    joined_at: date
    left_at: date | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddTripMemberResponse(BaseModel):
    status_code: int
    message: str
    data: TripMemberResponse


class TripMemberListResponse(BaseModel):
    members: list[TripMemberResponse]