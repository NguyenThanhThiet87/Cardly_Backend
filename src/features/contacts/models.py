from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class SocialLink(BaseModel):
    platform: str
    url: str


class ContactDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    owner_id: str
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
    is_favorite: bool = False
    scanned_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)
