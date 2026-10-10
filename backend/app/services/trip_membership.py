
from datetime import date
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_membership import TripMembershipModel
from app.repositories.trip_membership import TripMembershipRepository
from app.repositories.trips import TripRepository


class TripMembershipService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.membership_repo = TripMembershipRepository(db)
        self.trip_repo = TripRepository(db)

    async def create_membership(
        self,
        trip_id: uuid.UUID,
        display_name: str,
        current_user_id: uuid.UUID,
    ) -> tuple[TripMembershipModel, str]:
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        if trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can add members",
            )

        display_name = display_name.strip()

        if not display_name:
            raise HTTPException(
                status_code=422,
                detail="Member name cannot be empty",
            )

        membership = TripMembershipModel(
            trip_id=trip_id,
            user_id=None,
            display_name=display_name,
            joined_at=date.today(),
            status="ACTIVE",
        )

        await self.membership_repo.create(membership)

        result = await self.membership_repo.get_member_with_name(
            trip_id,
            membership.id,
        )

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Could not retrieve the created member",
            )

        return result

    async def get_all_members(
        self,
        trip_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> list[tuple[TripMembershipModel, str]]:
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        if not await self.trip_repo.is_member(trip_id, current_user_id) and trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this trip",
            )

        return await self.membership_repo.get_all_members_with_names(
            trip_id
        )

    async def get_member_by_id(
        self,
        trip_id: uuid.UUID,
        member_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> tuple[TripMembershipModel, str] | None:
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        if not await self.trip_repo.is_member(trip_id, current_user_id) and trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this trip",
            )

        return await self.membership_repo.get_member_with_name(
            trip_id,
            member_id,
        )


    async def remove_member(
        self,
        trip_id: uuid.UUID,
        member_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> tuple[TripMembershipModel, str]:
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        if trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can remove members",
            )

        member = await self.membership_repo.get_member_by_id(
            trip_id,
            member_id,
        )

        if member is None:
            raise HTTPException(
                status_code=404,
                detail="Member not found",
            )

        if member.user_id == trip.owner_id:
            raise HTTPException(
                status_code=400,
                detail="Trip owner cannot be removed",
            )

        if member.status != "ACTIVE":
            raise HTTPException(
                status_code=409,
                detail="Member is already inactive",
            )

        result = await self.membership_repo.remove_member_with_name(
            trip_id,
            member_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Member not found",
            )

        return result