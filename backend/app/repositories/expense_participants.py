from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.expense_participants import ExpenseParticipantModel
from app.models.trip_membership import TripMembershipModel
from app.models.users import UserModel



class ExpenseParticipantRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_participant(
        self,
        participant: ExpenseParticipantModel,
    ) -> ExpenseParticipantModel:

        self.db.add(participant)

        await self.db.flush()
        await self.db.refresh(participant)

        return participant

    async def get_participant_by_expense_id(
        self,
        expense_id,
    ) -> list[ExpenseParticipantModel]:

        stmt = select(ExpenseParticipantModel).where(
            ExpenseParticipantModel.expense_id == expense_id
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_participants_with_names_by_expense_id(
        self,
        expense_id,
    ) -> list[tuple[ExpenseParticipantModel, str]]:
        participant_name = func.coalesce(
            UserModel.name,
            TripMembershipModel.display_name,
        ).label("participant_name")

        stmt = (
            select(ExpenseParticipantModel, participant_name)
            .join(
                TripMembershipModel,
                ExpenseParticipantModel.trip_member_id == TripMembershipModel.id,
            )
            .outerjoin(
                UserModel,
                TripMembershipModel.user_id == UserModel.id,
            )
            .where(
                ExpenseParticipantModel.expense_id == expense_id
            )
        )

        result = await self.db.execute(stmt)

        return list(result.all())