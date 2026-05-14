from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict
from .constants import CONTACT_PLATFORM

class ContactButton(BaseModel):
    label: CONTACT_PLATFORM
    value: str = Field(..., example="https://facebook.com/thiet.nguyen")

# --- 1. BASE: Contains fields shared by both Request and Response ---
class DigitalCardBase(BaseModel):
    profile_url: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    contact_buttons: List[ContactButton] = Field(default_factory=list)
    bio: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    custom_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    qr_code_data: Optional[str] = None
    is_public: bool = Field(default=True)

# --- 2. CREATE: Used when creating a new document ---
class DigitalCardCreate(DigitalCardBase):
    pass

# --- 3. UPDATE: Used when updating (PATCH) ---
# Use an intermediate class technique to make all fields Optional
class DigitalCardUpdate(DigitalCardBase):
    # Override fields that are allowed to be updated, or keep defaults from Base
    # Note: Do not include view_count or updated_at here
    pass

# --- 4. RESPONSE: return data for Client ---
class DigitalCardResponse(DigitalCardBase):
    id: str = Field(alias="_id")
    owner_id: str
    view_count: int = Field(default=0)
    updated_at: datetime
    is_deleted: bool = Field(default=False)
    
    # Config for Pydantic to map from MongoDB Dict (with _id)
    model_config = ConfigDict(populate_by_name=True)