import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


# =========================
# REQUESTS
# =========================

class CreateTripRequest(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    start_date: date
    end_date: date

class UpdateTripRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_completed : bool | None = None

# =========================
# RESPONSES
# =========================

class TripResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    location: str | None
    start_date: date
    end_date: date
    is_completed: bool
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CreateTripResponse(BaseModel):
    status_code: int
    message : str
    data: TripResponse

class UpdateTripResponse(BaseModel):
    status_code: int
    message : str
    data: TripResponse

class GetTripByIdResponse(BaseModel):
    status_code: int
    message : str
    data: TripResponse

class TripListResponse(BaseModel):
    trips: list[TripResponse]