from app.models import trip_membership
from app.models import trip_membership
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import date

from app.models.trip_membership import TripMembershipModel

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
        
