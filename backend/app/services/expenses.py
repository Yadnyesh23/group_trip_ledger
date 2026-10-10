
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expenses import ExpenseModel, SplitType
from app.models.expense_participants import ExpenseParticipantModel
from app.models.expense_allocations import ExpenseAllocationModel
from app.repositories.expenses import ExpenseRepository
from app.repositories.expense_participants import ExpenseParticipantRepository
from app.repositories.expense_allocations import ExpenseAllocationRepository
from app.repositories.trips import TripRepository
from app.repositories.trip_membership import TripMembershipRepository
from app.services.allocation_engine import AllocationEngine


class ExpensesService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.participant_repo = ExpenseParticipantRepository(db)
        self.allocation_repo = ExpenseAllocationRepository(db)
        self.trip_repo = TripRepository(db)
        self.membership_repo = TripMembershipRepository(db)

    async def create_expense(
        self,
        trip_id: UUID,
        current_user_id: UUID,
        name: str,
        description: str | None,
        amount: Decimal,
        split_type: SplitType,
        category: str | None,
        paid_by_member_id: UUID,
        participant_member_ids: list[UUID],
        expense_date: date,
        custom_allocation: dict[UUID, Decimal] | None = None,
    ) -> tuple[ExpenseModel, str]:
        # 1. Verify trip exists
        trip = await self.trip_repo.get_trip_by_id(trip_id)
        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        # 2. Only the trip owner can create expenses
        if trip.owner_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can create expenses",
            )

        # 3. Verify payer is an active member of this trip
        payer = await self.membership_repo.get_member_by_id(
            trip_id,
            paid_by_member_id,
        )
        if payer is None:
            raise HTTPException(
                status_code=400,
                detail="Payer is not a member of this trip",
            )
        if payer.status != "ACTIVE":
            raise HTTPException(
                status_code=400,
                detail="Payer is not an active member of this trip",
            )

        # 4. Verify all participants are active members of this trip
        if not participant_member_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one participant is required",
            )

        # Reject duplicates
        if len(participant_member_ids) != len(set(participant_member_ids)):
            raise HTTPException(
                status_code=400,
                detail="Duplicate participants are not allowed",
            )

        for member_id in participant_member_ids:
            member = await self.membership_repo.get_member_by_id(
                trip_id,
                member_id,
            )
            if member is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Participant {member_id} is not a member of this trip",
                )
            if member.status != "ACTIVE":
                raise HTTPException(
                    status_code=400,
                    detail=f"Participant {member_id} is not an active member",
                )

        # 5. Calculate allocations
        try:
            allocations = AllocationEngine.calculate(
                expense_amount=amount,
                split_type=split_type,
                participant_member_ids=participant_member_ids,
                custom_allocation=custom_allocation,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

        # 6. Create expense (atomic: uses flush, not commit)
        expense = ExpenseModel(
            trip_id=trip_id,
            name=name,
            description=description,
            amount=amount,
            split_type=split_type,
            category=category,
            paid_by_member_id=paid_by_member_id,
            expense_date=expense_date,
        )
        expense = await self.expense_repo.create(expense)

        # 7. Create participant records
        for member_id in participant_member_ids:
            participant = ExpenseParticipantModel(
                expense_id=expense.id,
                trip_member_id=member_id,
            )
            await self.participant_repo.create_participant(participant)

        # 8. Create allocation records
        for member_id, alloc_amount in allocations.items():
            allocation = ExpenseAllocationModel(
                expense_id=expense.id,
                trip_member_id=member_id,
                amount=alloc_amount,
            )
            await self.allocation_repo.create(allocation)

        # 9. Commit all records atomically
        await self.db.commit()

        # 10. Return expense with payer name
        result = await self.expense_repo.get_expense_with_payer_name(
            trip_id,
            expense.id,
        )

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Could not retrieve the created expense",
            )

        return result

    async def get_all_expense_of_trip(
        self,
        current_user_id: UUID,
        trip_id: UUID,
    ) -> list[tuple[ExpenseModel, str]]:
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

        return await self.expense_repo.get_all_expenses_with_payer_names(
            trip_id
        )

    async def get_expense_by_id(
        self,
        current_user_id: UUID,
        trip_id: UUID,
        expense_id: UUID,
    ) -> tuple[ExpenseModel, str]:
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

        result = await self.expense_repo.get_expense_with_payer_name(
            trip_id,
            expense_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        return result