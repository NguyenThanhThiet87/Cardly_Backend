from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class EnrichmentResultBase(BaseModel):
    professional_brief: Optional[str] = None
    keywords: Optional[list[str]] = None
    highlights: Optional[list[str]] = None


class EnrichmentResultCreate(EnrichmentResultBase):
    contact_id: str


class EnrichmentResultUpdate(EnrichmentResultBase):
    pass


class EnrichmentResultResponse(EnrichmentResultCreate):
    id: str = Field(alias="_id")
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True)
