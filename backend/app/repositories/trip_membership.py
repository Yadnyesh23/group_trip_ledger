from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
import uuid

from app.models.trip_membership import TripMembershipModel
from app.models.users import UserModel

class TripMembershipRepository:
    def __init__(self,db : AsyncSession):
        self.db = db
    
    async def create(
        self,
        membership :TripMembershipModel 
        ) -> TripMembershipModel:
        
        self.db.add(membership)
        await self.db.flush()
        await self.db.refresh(membership)

        return membership
    
    async def get_all_members(
        self,
        trip_id
    ):
        stmt = select(TripMembershipModel).where(TripMembershipModel.trip_id == trip_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_member_by_id(
        self,
        trip_id,
        user_id
    ):
        stmt = select(TripMembershipModel).where(
            TripMembershipModel.trip_id == trip_id,
        TripMembershipModel.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def get_all_members_with_names(
        self,
        trip_id: uuid.UUID,
    ) -> list[tuple[TripMembershipModel, str]]:
        stmt = (
            select(TripMembershipModel, UserModel.name)
            .join(
                UserModel,
                TripMembershipModel.user_id == UserModel.id,
            )
            .where(TripMembershipModel.trip_id == trip_id)
        )

        result = await self.db.execute(stmt)
        return list(result.all())


    async def get_member_with_name(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> tuple[TripMembershipModel, str] | None:
        stmt = (
            select(TripMembershipModel, UserModel.name)
        .join(
            UserModel,
            TripMembershipModel.user_id == UserModel.id,
        )
        .where(
            TripMembershipModel.trip_id == trip_id,
            TripMembershipModel.user_id == user_id,
        )
    )

        result = await self.db.execute(stmt)
        return result.one_or_none()


    async def remove_member_with_name(
        self,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> tuple[TripMembershipModel, str] | None:
        member = await self.get_member_by_id(trip_id, user_id)

        if member is None:
            return None

        member.left_at = date.today()
        member.status = "LEFT"

        await self.db.flush()

        return await self.get_member_with_name(trip_id, user_id)
    
    async def remove_member(
        self,
        trip_id,
        member_id
    ):
        member = await self.get_member_by_id(trip_id, member_id)

        if member is None:
            return None
        
        member.left_at = date.today()
        member.status = "LEFT"

        await self.db.flush()
        await self.db.refresh(member)

        return member
        
