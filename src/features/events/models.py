from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    owner_id: str
    name: str
    location: Optional[str] = None
    event_type: Optional[str] = None
    event_date: datetime
    contact_ids: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
