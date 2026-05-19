from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EnrichmentResultCreate(BaseModel):
    contact_id: str
    professional_brief: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)


class EnrichmentResultUpdate(BaseModel):
    professional_brief: Optional[str] = None
    keywords: Optional[list[str]] = None
    highlights: Optional[list[str]] = None


class EnrichmentResultResponse(EnrichmentResultCreate):
    id: str = Field(alias="_id")
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True)
