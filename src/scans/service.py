from database import get_db
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from .models import BusinessCardScanDocument
from .utils import extract_text_fields
from .constants import STATUS_DONE, STATUS_FAILED

COLLECTION = "business_card_scans"


async def run_ocr(image_data: bytes) -> tuple[str, float]:
    # TODO: integrate AWS Textract or Tesseract
    # Returns (raw_text, confidence_score)
    raise NotImplementedError("OCR not implemented yet")


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
