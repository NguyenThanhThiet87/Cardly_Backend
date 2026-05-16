from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ExtractedCardData(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    phones: Optional[list[str]] = None
    emails: Optional[list[str]] = None
    website: Optional[str] = None
    address: Optional[str] = None

class ScanResponse(BaseModel):
    id: str = Field(alias="_id")
    image_url: str
    status: str
    raw_text: Optional[str] = None
    extracted_data: Optional[ExtractedCardData] = None
    confidence_score: Optional[float] = None
    created_at: datetime
