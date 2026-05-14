from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(UserProfile):
    is_active: bool
    created_at: datetime
