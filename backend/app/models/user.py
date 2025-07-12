from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    company: Optional[str] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    createdAt: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserBase):
    id: str
    hashed_password: str
    createdAt: datetime
    updatedAt: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    refreshToken: str

class RefreshTokenRequest(BaseModel):
    refreshToken: str