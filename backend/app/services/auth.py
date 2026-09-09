from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.repositories.users import UserRepository
from app.models.users import UserModel
from app.core.hash_pass import hash_password

class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register_user(self, user : UserModel):
        user_exist = await self.user_repo.get_by_email(user.email)
        
        if user_exist:
            raise ValueError("User already exists")
    
        hashed_password = hash_password(user.password)

        new_user = UserModel(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password
        )

        await self.user_repo.create(new_user)
        return new_user
