from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import jwt

from app.core.security import bearer_scheme
from app.database.db import get_db
from app.core.config import settings
from app.repositories.users import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_repo = UserRepository(db)

    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return user

async def get_user_from_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

 
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

   
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    
    refresh_token_repo = RefreshTokenRepository(db)

    refresh_token = await refresh_token_repo.get_by_token(token)

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

   
    if refresh_token.revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked"
        )

   
    user_repo = UserRepository(db)

    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    return user