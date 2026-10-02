from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.trips import (
    CreateTripRequest,
    CreateTripResponse,
    TripResponse,
    UpdateTripRequest,
    UpdateTripResponse,
    GetTripByIdResponse
)
from app.models.users import UserModel
from app.core.dependencies import get_current_user
from app.database.db import get_db
from app.services.trips import TripService


router = APIRouter(
    prefix="/api/v1",
    tags=["Trip"]
)


# --------------------------------------------------
# CREATE TRIP
# --------------------------------------------------

@router.post("/trips", response_model=CreateTripResponse)
async def create_trip(
    request: CreateTripRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip_service = TripService(db)

    new_trip = await trip_service.create_trip(
        current_user.id,
        request.name,
        request.description,
        request.location,
        request.start_date,
        request.end_date,
    )

    return CreateTripResponse(
        status_code=201,
        message="Trip created successfully",
        data=TripResponse(
            id=new_trip.id,
            name=new_trip.name,
            description=new_trip.description,
            location=new_trip.location,
            owner_id=new_trip.owner_id,
            start_date=new_trip.start_date,
            end_date=new_trip.end_date,
            is_completed=new_trip.is_completed,
            created_at=new_trip.created_at,
            updated_at=new_trip.updated_at,
        ),
    )


# --------------------------------------------------
# GET TRIP BY ID
# --------------------------------------------------

@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip_by_id(
    trip_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip_service = TripService(db)

    trip = await trip_service.get_trip_by_id(
        trip_id,
        current_user.id,
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found",
        )

    return  TripResponse(
        id=trip.id,
        name=trip.name,
        description=trip.description,
        location=trip.location,
        owner_id=trip.owner_id,
        start_date=trip.start_date,
        end_date=trip.end_date,
        is_completed=trip.is_completed,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )


# --------------------------------------------------
# GET ALL TRIPS OWNED BY USER
# --------------------------------------------------

@router.get("/trips", response_model=list[TripResponse])
async def get_my_trips(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip_service = TripService(db)

    trips = await trip_service.get_trips_by_owner(
        current_user.id
    )

    return [
        TripResponse(
            id=trip.id,
            name=trip.name,
            description=trip.description,
            location=trip.location,
            owner_id=trip.owner_id,
            start_date=trip.start_date,
            end_date=trip.end_date,
            is_completed=trip.is_completed,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )
        for trip in trips
    ]


# --------------------------------------------------
# UPDATE TRIP
# --------------------------------------------------

@router.patch(
    "/trips/{trip_id}",
    response_model=UpdateTripResponse,
)
async def update_trip(
    trip_id: uuid.UUID,
    data: UpdateTripRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip_service = TripService(db)

    trip = await trip_service.get_trip_by_id(
        trip_id,
        current_user.id,
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found",
        )

    updated_trip = await trip_service.update_trip(
        trip_id,
        current_user.id,
        data,
    )

    return UpdateTripResponse(
       status_code = 201,
       message = "Trip updated succesfully.",
       data =TripResponse(
        id=updated_trip.id,
        name=updated_trip.name,
        description=updated_trip.description,
        location=updated_trip.location,
        owner_id=updated_trip.owner_id,
        start_date=updated_trip.start_date,
        end_date=updated_trip.end_date,
        is_completed=updated_trip.is_completed,
        created_at=updated_trip.created_at,
        updated_at=updated_trip.updated_at,
       )
    )


# --------------------------------------------------
# DELETE TRIP
# --------------------------------------------------

@router.delete("/trips/{trip_id}")
async def delete_trip(
    trip_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip_service = TripService(db)

    trip = await trip_service.get_trip_by_id(
        trip_id,
        current_user.id,
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found",
        )

    await trip_service.delete_trip(
        trip_id,
        current_user.id,
    )

    return {
        "status_code": 200,
        "message": "Trip deleted successfully",
    }
