import uuid
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.trips import TripRepository
from app.repositories.trip_membership import TripMembershipRepository
from app.repositories.expenses import ExpenseRepository
from app.repositories.expense_participants import ExpenseParticipantRepository
from app.repositories.expense_allocations import ExpenseAllocationRepository

from app.models.expenses import ExpenseModel
from app.models.expense_participants import ExpenseParticipantModel
from app.models.expense_allocations import ExpenseAllocationModel

from app.services.allocation_engine import AllocationEngine


class ExpensesService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.trip_repo = TripRepository(db)
        self.trip_membership_repo = TripMembershipRepository(db)
        self.expense_participant_repo = ExpenseParticipantRepository(db)
        self.expense_allocation_repo = ExpenseAllocationRepository(db)

    async def create_expense(
        self,
        trip_id: uuid.UUID,
        current_user_id: uuid.UUID,
        name: str,
        description: str | None,
        amount,
        split_type,
        category: str | None,
        paid_by_user_id: uuid.UUID,
        participant_user_ids: list[UUID],
        expense_date,
        custom_allocation: dict[UUID, object] | None = None,
    ) -> ExpenseModel:

        # ---------------------------------
        # 1. Check trip
        # ---------------------------------

        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        # ---------------------------------
        # 2. Check owner
        # ---------------------------------

        if current_user_id != trip.owner_id:
            raise HTTPException(
                status_code=403,
                detail="Only the trip owner can add expenses"
            )

        # ---------------------------------
        # 3. Check payer
        # ---------------------------------

        payer_membership = (
            await self.trip_membership_repo.get_member_by_id(
                trip_id,
                paid_by_user_id
            )
        )

        if (
            payer_membership is None
            or payer_membership.status != "ACTIVE"
        ):
            raise HTTPException(
                status_code=400,
                detail="The payer is not an active member of the trip"
            )

        # ---------------------------------
        # 4. Validate participants
        # ---------------------------------

        if not participant_user_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one participant is required"
            )

        if len(participant_user_ids) != len(set(participant_user_ids)):
            raise HTTPException(
                status_code=400,
                detail="Duplicate participants are not allowed"
            )

        for participant_id in participant_user_ids:

            membership = (
                await self.trip_membership_repo.get_member_by_id(
                    trip_id,
                    participant_id
                )
            )

            if (
                membership is None
                or membership.status != "ACTIVE"
            ):
                raise HTTPException(
                    status_code=400,
                    detail="All participants must be active members of the trip"
                )

        # ---------------------------------
        # 5. Calculate allocations
        # ---------------------------------

        try:
            allocations = AllocationEngine.calculate(
                expense_amount=amount,
                split_type=split_type,
                participant_user_ids=participant_user_ids,
                custom_allocation=custom_allocation,
            )

        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

        # ---------------------------------
        # 6. Create expense
        # ---------------------------------

        expense = ExpenseModel(
            trip_id=trip_id,
            name=name,
            description=description,
            amount=amount,
            split_type=split_type,
            category=category,
            paid_by_user_id=paid_by_user_id,
            expense_date=expense_date,
        )

        new_expense = await self.expense_repo.create(expense)

        # ---------------------------------
        # 7. Create participant records
        # ---------------------------------

        for participant_id in participant_user_ids:

            participant = ExpenseParticipantModel(
                expense_id=new_expense.id,
                user_id=participant_id,
            )

            await self.expense_participant_repo.create_participant(
                participant
            )

        # ---------------------------------
        # 8. Create allocation records
        # ---------------------------------

        for user_id, allocated_amount in allocations.items():

            allocation = ExpenseAllocationModel(
                expense_id=new_expense.id,
                user_id=user_id,
                amount=allocated_amount,
            )

            await self.expense_allocation_repo.create(allocation)

        

        # ---------------------------------
        # 9. Commit everything
        # ---------------------------------

        await self.db.commit()

        # Refresh expense after commit
        await self.db.refresh(new_expense)

        result = await self.expense_repo.get_expense_with_payer_name(
        trip_id=trip_id,
        expense_id=new_expense.id,
        )

        return result
    
    async def get_expense_by_id(
        self,
        current_user_id,
        trip_id,
        expense_id
        ):

        trip = await self.trip_repo.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if current_user_id != trip.owner_id:
            raise HTTPException(status_code=403, detail="Only owner can see expenses")
        
        expense = await self.expense_repo.get_expense_with_payer_name(
            trip_id,
            expense_id,
        )

        if expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        return expense
    

    async def get_all_expense_of_trip(
        self, 
        current_user_id,
        trip_id
    ):
        trip = await self.trip_repo.get_trip_by_id(trip_id)

        

        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if current_user_id != trip.owner_id:
            raise HTTPException(status_code=403, detail="Only owner can see expenses")
        
        expenses = (
            await self.expense_repo.get_all_expenses_with_payer_names(trip_id)
        )

        if len(expenses) == 0:
            raise HTTPException(status_code=404, detail="Expenses list is empty")
        
        return expenses
        