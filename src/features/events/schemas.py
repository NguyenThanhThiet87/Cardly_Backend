from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    name: str
    location: Optional[str] = None
    event_type: Optional[str] = None
    event_date: datetime
    contact_ids: list[str] = Field(default_factory=list)


class EventUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    contact_ids: Optional[list[str]] = None


class EventResponse(EventCreate):
    id: str = Field(alias="_id")
    owner_id: str

    model_config = ConfigDict(populate_by_name=True)
