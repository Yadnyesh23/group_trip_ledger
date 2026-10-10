from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select, func

from app.repositories.expenses import ExpenseRepository
from app.repositories.expense_allocations import ExpenseAllocationRepository
from app.repositories.trips import TripRepository
from app.repositories.trip_membership import TripMembershipRepository
from app.services.balance_engine import BalanceEngine
from app.models.trip_membership import TripMembershipModel
from app.models.users import UserModel


class BalanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.allocation_repo = ExpenseAllocationRepository(db)
        self.trip_repo = TripRepository(db)
        self.membership_repo = TripMembershipRepository(db)

    async def get_balance_of_trip(self, trip_id: UUID, current_user_id: UUID) -> list[dict]:
        trip = await self.trip_repo.get_trip_by_id(trip_id)
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        if not await self.trip_repo.is_member(trip_id, current_user_id) and trip.owner_id != current_user_id:
            raise HTTPException(status_code=403, detail="You are not a member of this trip")

        expenses = await self.expense_repo.get_all_expenses_of_trip(trip_id)
        allocations = await self.allocation_repo.get_all_allocations_by_trip(trip_id)

        if not expenses:
            # Return zero balances for all active members
            members_with_names = await self.membership_repo.get_all_members_with_names(trip_id)
            return [
                {
                    "member_id": member.id,
                    "member_name": user_name,
                    "balance": 0,
                }
                for member, user_name in members_with_names
                if member.status == "ACTIVE"
            ]

        balances = BalanceEngine.calculate_balances(
            [
                {"id": e.id, "name": e.name, "amount": e.amount,
                 "paid_by_member_id": e.paid_by_member_id}
                for e in expenses
            ],
            [
                {"expense_id": a.expense_id, "member_id": a.trip_member_id, "amount": a.amount}
                for a in allocations
            ],
        )

        member_names = await self._get_member_names(trip_id)

        # Include all active members (even those with zero balance)
        all_members = await self.membership_repo.get_all_members_with_names(trip_id)
        result = []
        seen_member_ids = set()

        # First add members with non-zero balances
        for mid, bal in balances.items():
            seen_member_ids.add(mid)
            result.append({
                "member_id": mid,
                "member_name": member_names.get(mid, "Unknown member"),
                "balance": bal,
            })

        # Then add active members with zero balance
        for member, user_name in all_members:
            if member.id not in seen_member_ids and member.status == "ACTIVE":
                result.append({
                    "member_id": member.id,
                    "member_name": user_name,
                    "balance": 0,
                })

        return result

    async def _get_member_names(
        self,
        trip_id: UUID,
    ) -> dict[UUID, str]:
        """Resolve member_id -> display name for all members in a trip."""
        members_with_names = await self.membership_repo.get_all_members_with_names(trip_id)
        return {
            member.id: user_name
            for member, user_name in members_with_names
        }