from datetime import date
import uuid
from uuid import UUID

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trips import TripModel
from app.models.trip_membership import TripMembershipModel
from app.models.users import UserModel

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
    
    async def is_member(self, trip_id: UUID, user_id: UUID) -> bool:
        stmt = select(
            exists().where(
                TripMembershipModel.trip_id == trip_id,
                TripMembershipModel.user_id == user_id,
            )
    )
        return bool(await self.db.scalar(stmt))
    
    
    async def get_trip_with_owner_name(
        self,
        trip_id: uuid.UUID,
    ) -> tuple[TripModel, str] | None:
        stmt = (
            select(TripModel, UserModel.name)
            .join(
                UserModel,
                TripModel.owner_id == UserModel.id,
             )
            .where(TripModel.id == trip_id)
        )

        result = await self.db.execute(stmt)
        return result.one_or_none()


    async def get_trips_owned_by_user_with_owner_names(
        self,
        user_id: uuid.UUID,
    ) -> list[tuple[TripModel, str]]:
        stmt = (
            select(TripModel, UserModel.name)
            .join(
                UserModel,
                TripModel.owner_id == UserModel.id,
            )
            .where(TripModel.owner_id == user_id)
        )

        result = await self.db.execute(stmt)
        return list(result.all())


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