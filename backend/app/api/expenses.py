from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import UserModel
from app.services.expenses import ExpensesService
from app.schemas.expenses import ExpenseCreateRequest, ExpenseResponse, ExpenseListResponse


router = APIRouter(
    prefix="/api/v1/trips/{trip_id}",
    tags=["Expenses"]
)


@router.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    trip_id: UUID,
    request: ExpenseCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    expense_service = ExpensesService(db)

    expense = await expense_service.create_expense(
        trip_id=trip_id,
        current_user_id=current_user.id,
        name=request.name,
        description=request.description,
        amount=request.amount,
        split_type=request.split_type,
        category=request.category,
        paid_by_user_id=request.paid_by_user_id,
        participant_user_ids=request.participant_user_ids,
        expense_date=request.expense_date,
        custom_allocation=request.custom_allocation,
    )

    return expense

@router.get(
    "/expenses",
    response_model=ExpenseListResponse,
    status_code=status.HTTP_200_OK
    )
async def get_expense_for_trip(
    trip_id : UUID,
    current_user : UserModel = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    expense_service = ExpensesService(db)

    expenses = await expense_service.get_all_expense_of_trip(current_user.id, trip_id)

    return ExpenseListResponse(
        total_expenses = len(expenses),
        expenses = [
            ExpenseResponse(
                id = expense.id,
                trip_id = expense.trip_id,
                name = expense.name,
                description = expense.description,
                amount = expense.amount,
                split_type = expense.split_type,
                category = expense.category,
                paid_by_user_id = expense.paid_by_user_id,
                expense_date = expense.expense_date,
                created_at = expense.created_at,
                updated_at = expense.updated_at
            )
            for expense in expenses
        ]
    )

@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK
)
async def get_expense_by_id(
    trip_id:UUID,
    expense_id:UUID,
    current_user : UserModel = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    expense_service = ExpensesService(db)

    expense = await expense_service.get_expense_by_id(current_user.id, trip_id, expense_id)

    return ExpenseResponse(
        id = expense.id,
        trip_id = expense.trip_id,
        name = expense.name,
        description = expense.description,
        amount = expense.amount,
        split_type = expense.split_type,
        category = expense.category,
        paid_by_user_id = expense.paid_by_user_id,
        expense_date = expense.expense_date,
        created_at = expense.created_at,
        updated_at = expense.updated_at
    )