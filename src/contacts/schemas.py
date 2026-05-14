from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from .models import SocialLink


class ContactCreate(BaseModel):
    full_name: str
    position: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    source_note: Optional[str] = None
    social_links: List[SocialLink] = []
    tag_ids: List[str] = []


class ContactUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    source_note: Optional[str] = None
    social_links: Optional[List[SocialLink]] = None
    tag_ids: Optional[List[str]] = None


class ContactFilter(BaseModel):
    tag: Optional[str] = None
    search: Optional[str] = None


class ContactResponse(ContactCreate):
    id: str = Field(alias="_id")
    owner_id: str
    is_favorite: bool
    qr_code_data: Optional[str] = None
    scanned_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)
