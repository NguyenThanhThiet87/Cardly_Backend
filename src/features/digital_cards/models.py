from typing import Optional, List, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, HttpUrl

class DigitalCardModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    owner_id: str
    profile_url: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    contact_buttons: List[Dict[str, str]] = Field(default_factory=list)
    bio: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    custom_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    theme: Dict = Field(default_factory=dict)
    qr_code_data: Optional[str] = None
    view_count: int = Field(default=0)
    is_public: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)