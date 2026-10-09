from app.api import trips
from app.api import trips
from app.api import trips
from app.api import trips
from datetime import date
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_membership import TripMembershipModel
from app.repositories.trip_membership import TripMembershipRepository
from app.repositories.trips import TripRepository
from app.repositories.users import UserRepository


class TripMembershipService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.membership_repo = TripMembershipRepository(db)
        self.trip_repo = TripRepository(db)
        self.user_repo = UserRepository(db)

    async def create_membership(
        self,
        trip_id,
        user_id,
        current_user_id,
    ):
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        if trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can add members"
            )

        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        existing_membership = await self.membership_repo.get_member_by_id(
            trip_id=trip_id,
            user_id=user_id,
        )

        if existing_membership is not None:
            raise HTTPException(
                status_code=409,
                detail="User is already a member of this trip"
            )

        membership = TripMembershipModel(
            trip_id=trip_id,
            user_id=user_id,
            joined_at=date.today(),
            status="ACTIVE",
        )

        await self.membership_repo.create(membership)

        return await self.membership_repo.get_member_with_name(
            trip_id,
            user_id,
        )
    
    async def get_all_members(
        self,
        trip_id
    )->list[tuple[TripMembershipModel, str]]:
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404, 
                detail="Trip not found"
            )
        return await self.membership_repo.get_all_members_with_names(
    trip_id
)
    
    async def get_member_by_id(
        self, 
        trip_id,
        user_id
    )-> tuple[TripMembershipModel, str] | None:
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404, 
                detail="Trip not found"
            )

        return await self.membership_repo.get_member_with_name(
    trip_id,
    user_id,
)
    
    async def remove_member(
        self,
        trip_id,
        member_id,
        current_user_id
    ):
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        if trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can remove members"
            )
        if member_id == trip.owner_id:
            raise HTTPException(
            status_code=400,
            detail="Trip owner cannot be removed"
        )

        member = await self.membership_repo.remove_member_with_name(
    trip_id,
    member_id,
)

        if member is None:
            raise HTTPException(
                status_code=404,
                detail="Member not found"
            )


        await self.db.commit()

        return member

        