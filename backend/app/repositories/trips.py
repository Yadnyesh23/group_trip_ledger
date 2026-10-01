import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trips import TripModel


class TripRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trip(
        self,
        trip : TripModel
    ) -> TripModel:

        self.db.add(trip)
        await self.db.commit()
        await self.db.refresh(trip)
        return trip

    async def get_trip_by_id(
        self,
        trip_id: uuid.UUID,
    ) -> TripModel | None:

        stmt = select(TripModel).where(
            TripModel.id == trip_id
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_trips_owned_by_user(
        self,
        user_id: uuid.UUID,
    ) -> list[TripModel]:

        stmt = select(TripModel).where(
            TripModel.owner_id == user_id
        )

        result = await self.db.execute(stmt)

        return result.scalars().all()

    async def update_trip(
        self,
        trip_id: uuid.UUID,
        data: dict,
    ) -> TripModel | None:

        trip = await self.get_trip_by_id(trip_id)

        if not trip:
            return None

        for key, value in data.items():
            setattr(trip, key, value)

        await self.db.commit()
        await self.db.refresh(trip)

        return trip

    async def delete_trip(
        self,
        trip_id: uuid.UUID,
    ) -> TripModel | None:

        trip = await self.get_trip_by_id(trip_id)

        if not trip:
            return None

        await self.db.delete(trip)
        await self.db.commit()

        return trip