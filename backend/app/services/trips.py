import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trips import TripModel
from app.models.trip_membership import TripMembershipModel
from app.repositories.trips import TripRepository
from app.repositories.trip_membership import TripMembershipRepository
from app.schemas.trips import UpdateTripRequest

class TripService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.trip_repo = TripRepository(db)
        self.membership_repo = TripMembershipRepository(db)

    async def create_trip(
        self,
        user_id: uuid.UUID,
        name: str,
        description: str | None,
        location: str | None,
        start_date: date,
        end_date: date,
    ) -> TripModel:

        
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be after end date"
            )

        trip = TripModel(
            name=name,
            description=description,
            location=location,
            start_date=start_date,
            end_date=end_date,
            is_completed=False,
            owner_id=user_id,
        )

        trip = await self.trip_repo.create_trip(trip)

        membership = TripMembershipModel(
                trip_id=trip.id,
                user_id=user_id,
                joined_at=date.today(),
                status="ACTIVE",
            )
        await self.membership_repo.create(membership)
        await self.db.commit()
        return trip

    async def get_trip_by_id(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TripModel:

        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        if trip.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this trip"
            )

        return trip

    async def get_trips_by_owner(
        self,
        user_id: uuid.UUID,
    ) -> list[TripModel]:

        return await self.trip_repo.get_trips_owned_by_user(user_id)

    async def update_trip(
    self,
    trip_id: uuid.UUID,
    user_id: uuid.UUID,
    data: UpdateTripRequest,
) -> TripModel:

        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        if trip.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can update this trip"
            )

    # Only fields actually sent by the client
        update_data = data.model_dump(
            exclude_unset=True
        )

    # Nothing to update
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

    # Validate dates using existing values when not provided
        new_start_date = update_data.get(
            "start_date",
            trip.start_date
        )

        new_end_date = update_data.get(
            "end_date",
            trip.end_date
         )

        if new_start_date > new_end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be after end date"
            )

        updated_trip = await self.trip_repo.update_trip(
            trip_id,
            update_data
        )

        return updated_trip

    async def delete_trip(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TripModel:

        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        if trip.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can delete this trip"
            )

        deleted_trip = await self.trip_repo.delete_trip(trip_id)

        return deleted_trip