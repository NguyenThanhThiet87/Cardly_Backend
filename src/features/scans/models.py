from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class BusinessCardScanDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    contact_id: Optional[str] = None
    image_url: str
    raw_text: Optional[str] = None
    extracted_data: Optional[dict] = None
    confidence_score: Optional[float] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)
