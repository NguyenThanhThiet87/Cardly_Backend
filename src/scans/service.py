from database import get_db
import os
import httpx
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from .models import BusinessCardScanDocument
from .utils import extract_text_fields
from .constants import STATUS_DONE, STATUS_FAILED

COLLECTION = "business_card_scans"

async def run_ocr(image_data: bytes) -> tuple[str, dict, float]:
    base_url = os.getenv("PADDLEOCR_VL_SERVER_URL")
    if not base_url:
        raise ValueError("PADDLEOCR_VL_SERVER_URL is not set")
    url = base_url.rstrip("/") + "/predict"
    
    token = os.getenv("ACCESS_TOKEN_PADDLEOCR_VL")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient() as client:
        files = {"file": ("card.jpg", image_data, "image/jpeg")}
        try:
            response = await client.post(url, headers=headers, files=files, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            
            raw_text = data.get("raw_text", "")
            extracted_data = data.get("extracted_data", {})
            confidence = data.get("confidence_score", 0.9)
            
            return raw_text, extracted_data, confidence
            
        except httpx.HTTPStatusError as e:
            print(f"Hugging Face API returned error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Error calling Hugging Face API: {e}")
            raise

async def save_scan(
    image_url: str,
    raw_text: str,
    extracted_data: dict,
    confidence_score: float,
    contact_id: str | None = None,
) -> dict:
    db = await get_db()
    doc = BusinessCardScanDocument(
        contact_id=contact_id,
        image_url=image_url,
        raw_text=raw_text,
        extracted_data=extracted_data,
        confidence_score=confidence_score,
        status=STATUS_DONE,
    )
    result = await db[COLLECTION].insert_one(doc.model_dump(mode="json", exclude_none=True))
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return jsonable_encoder(created, custom_encoder={ObjectId: str})
