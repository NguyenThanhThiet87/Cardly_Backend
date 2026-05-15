from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema (without password)"""
    id: str
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: str

    class Config:
        populate_by_name = True


class AuthResponse(BaseModel):
    """Authentication response with user and token"""
    user: UserResponse
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str
