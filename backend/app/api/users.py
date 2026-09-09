from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegisterRequest, RegisterResponse
from app.services.auth import AuthService
from app.database.db import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    new_user = await auth_service.register_user(request)
    return RegisterResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )
