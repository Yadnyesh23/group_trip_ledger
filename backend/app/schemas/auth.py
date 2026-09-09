from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


# =========================
# REQUESTS
# =========================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# RESPONSES
# =========================

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class RegisterResponse(BaseModel):
    statuscode : int
    message : str
    data : UserResponse


class LoginResponse(BaseModel):
    statuscode : int
    message : str
    tokens : TokenResponse


class MeResponse(BaseModel):
    status_code : int
    message : str
    data : UserResponse