from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.trips import TripRepository
from app.repositories.expenses import ExpenseRepository
from app.repositories.expense_allocations import ExpenseAllocationRepository
from app.repositories.trip_membership import TripMembershipRepository

from app.services.balance import BalanceService
from app.services.settlement import SettlementService


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

        self.trip_repository = TripRepository(db)
        self.expense_repository = ExpenseRepository(db)
        self.allocation_repository = ExpenseAllocationRepository(db)
        self.trip_membership_repository = TripMembershipRepository(db)

        self.balance_service = BalanceService(db)
        self.settlement_service = SettlementService(db)

    async def generate_report(
        self,
        current_user_id: UUID,
        trip_id: UUID,
    ) -> dict:
        # 1. Check whether the trip exists.
        trip = await self.trip_repository.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        # 2. Check whether the current user can access the report.
        is_member = await self.trip_repository.is_member(
            trip_id,
            current_user_id,
        )

        if not is_member and trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Not a member of this trip",
            )

        # 3. Retrieve trip members together with their names.
        members_with_names = (
            await self.trip_membership_repository
            .get_all_members_with_names(trip_id)
        )

        members = [
            {
                "id": member.id,
                "trip_id": member.trip_id,
                "user_id": member.user_id,
                "user_name": user_name,
                "joined_at": member.joined_at,
                "left_at": member.left_at,
                "status": member.status,
                "created_at": member.created_at,
                "updated_at": member.updated_at,
            }
            for member, user_name in members_with_names
        ]

        # 4. Retrieve expenses together with each payer's name.
        expenses_with_payer_names = (
            await self.expense_repository
            .get_all_expenses_with_payer_names(trip_id)
        )

        # 5. Retrieve allocations together with each member's name.
        allocations_with_names = (
            await self.allocation_repository
            .get_all_allocations_with_names_by_trip(trip_id)
        )

        # Group allocations by expense ID.
        allocations_by_expense: dict[UUID, list[dict]] = {}

        for allocation, user_name in allocations_with_names:
            allocations_by_expense.setdefault(
                allocation.expense_id,
                [],
            ).append(
                {
                    "member_id": allocation.trip_member_id,
                    "member_name": user_name,
                    "amount": allocation.amount,
                }
            )

        # 6. Build the report's expense data.
        formatted_expenses = [
            {
                "id": expense.id,
                "trip_id": expense.trip_id,
                "name": expense.name,
                "description": expense.description,
                "amount": expense.amount,
                "split_type": expense.split_type,
                "category": expense.category,
                "paid_by_member_id": expense.paid_by_member_id,
                "paid_by_name": payer_name,
                "expense_date": expense.expense_date,
                "allocations": allocations_by_expense.get(
                    expense.id,
                    [],
                ),
            }
            for expense, payer_name in expenses_with_payer_names
        ]

        # 7. Calculate trip balances.
        balances = await self.balance_service.get_balance_of_trip(
            trip_id,
            current_user_id,
        )

        # 8. Calculate suggested settlements.
        settlements = await self.settlement_service.get_settlements(
            current_user_id,
            trip_id,
        )

        # 9. Return the complete report data.
        return {
            "members": members,
            "expenses": formatted_expenses,
            "allocations": [
                {
                    "expense_id": allocation.expense_id,
                    "member_id": allocation.trip_member_id,
                    "member_name": user_name,
                    "amount": allocation.amount,
                }
                for allocation, user_name in allocations_with_names
            ],
            "balances": balances,
            "settlements": settlements,
        }
