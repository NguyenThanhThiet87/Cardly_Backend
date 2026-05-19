from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .models import SocialLink


def _normalize_list_fields(data: dict) -> dict:
    # Map singular to plural if plural is missing
    if "email" in data and "emails" not in data:
        data["emails"] = data.pop("email")
    if "phone" in data and "phones" not in data:
        data["phones"] = data.pop("phone")

    for field in ("emails", "phones"):
        val = data.get(field)
        if isinstance(val, str):
            data[field] = [val]
        elif val is None:
            data[field] = []
    return data

class ContactCreate(BaseModel):
    full_name: str
    position: Optional[str] = None
    company: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    website: Optional[str] = None
    address: Optional[str] = None
    qr_code_data: Optional[str] = None
    notes: Optional[str] = None
    source_note: Optional[str] = None
    social_links: List[SocialLink] = Field(default_factory=list)
    tag_ids: List[str] = Field(default_factory=list)
    scanned_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def support_legacy_fields(cls, data):
        if isinstance(data, dict):
            return _normalize_list_fields(data)
        return data

class ContactUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    emails: Optional[List[str]] = None
    phones: Optional[List[str]] = None
    website: Optional[str] = None
    address: Optional[str] = None
    qr_code_data: Optional[str] = None
    notes: Optional[str] = None
    source_note: Optional[str] = None
    social_links: Optional[List[SocialLink]] = None
    tag_ids: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def support_legacy_list_fields(cls, data):
        if isinstance(data, dict):
            return _normalize_list_fields(data)
        return data


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
