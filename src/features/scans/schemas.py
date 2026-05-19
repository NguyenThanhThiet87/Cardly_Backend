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
    confidence: Optional[float] = None

class ScanResponse(BaseModel):
    id: str = Field(alias="_id")
    image_url: str
    status: str
    raw_text: Optional[str] = None
    extracted_data: Optional[ExtractedCardData] = None
    created_at: datetime
