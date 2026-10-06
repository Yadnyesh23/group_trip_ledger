from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.expense_participants import ExpenseParticipantModel

class ExpenseParticipantRepository:

    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_participant(
        self,
        participant : ExpenseParticipantModel
    ) -> ExpenseParticipantModel:

        self.db.add(participant)
        
        await self.db.flush()
        await self.db.refresh(participant)
    
        return participant
    
    async def get_participant_by_expense_id(
        self,
        expense_id,
    )-> list[ExpenseParticipantModel]:

        stmt = select(ExpenseParticipantModel).where(ExpenseParticipantModel.expense_id == expense_id)
        
        result = await self.db.execute(stmt)
        
        return list(result.scalars().all())


