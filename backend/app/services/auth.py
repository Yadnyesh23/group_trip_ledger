from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.repositories.users import UserRepository
from app.models.users import UserModel
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
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
    
    async def login_user(self, email, password):
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ValueError("User not found")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid password")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "token_type" : "bearer"
        }
    
    
