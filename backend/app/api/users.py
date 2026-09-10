from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    UserResponse,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    MeResponse,
    LogoutResponse
)
from app.services.auth import AuthService
from app.database.db import get_db
from app.core.dependencies import get_current_user, get_user_from_refresh_token
from app.core.security import create_access_token
from app.models.users import UserModel

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    new_user = await auth_service.register_user(request.name, request.email, request.password)
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

@router.get("/me")
async def get_me(
    current_user: UserModel = Depends(get_current_user)
):
    return MeResponse(
        status_code=200,
        message="User fetched successfully",
        data = UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
    )
    )

@router.post('/logout')
async def logout(
    current_user : UserModel = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    auth_service = AuthService(db)
    await auth_service.logout_user(user_id)
    return LogoutResponse(
        status_code = 200,
        message = "User logged out successfully"
    )
   
@router.post("/refresh")
async def refresh_token(
    current_user: UserModel = Depends(get_user_from_refresh_token)
):
    new_access_token = create_access_token(current_user.id)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }