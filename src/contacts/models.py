from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .constants import PHONE_TYPE_PERSONAL, PHONE_TYPES


class SocialLink(BaseModel):
    platform: str
    url: str


class PhoneNumber(BaseModel):
    type: str = PHONE_TYPE_PERSONAL
    number: str
    label: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in PHONE_TYPES:
            return PHONE_TYPE_PERSONAL
        return value


class ContactDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    owner_id: str
    full_name: str
    position: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone_numbers: List[PhoneNumber] = Field(default_factory=list)
    website: Optional[str] = None
    address: Optional[str] = None
    qr_code_data: Optional[str] = None
    notes: Optional[str] = None
    source_note: Optional[str] = None
    social_links: List[SocialLink] = Field(default_factory=list)
    tag_ids: List[str] = Field(default_factory=list)
    is_favorite: bool = False
    scanned_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)
