from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserDocument(BaseModel):
    """User document model for MongoDB"""
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    exp: int
    iat: int
    type: str  # 'access' or 'refresh'
