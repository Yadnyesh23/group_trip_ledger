from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegisterRequest, RegisterResponse, UserResponse, LoginRequest, LoginResponse, TokenResponse
from app.services.auth import AuthService
from app.database.db import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    new_user = await auth_service.register_user(request)
    return RegisterResponse(
        statuscode = 201,
        message = "User registered successfully",
        data = UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
    )

@router.post('/login', response_model = LoginResponse)
async def login(request : LoginRequest, db : AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    tokens = await auth_service.login_user(request.email, request.password)
    return LoginResponse(
        statuscode = 200,
        message = "User logged in successfully",
        tokens = TokenResponse(
            access_token = tokens["access_token"],
            refresh_token = tokens["refresh_token"],
            token_type = tokens["token_type"]
        )
    )

