from src.database import get_db
import os
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from .models import BusinessCardScanDocument
from .utils import extract_text_fields
from .constants import STATUS_DONE, STATUS_FAILED

COLLECTION = "business_card_scans"

import io
import json
from google import genai
from PIL import Image

from google.genai import types

from dotenv import load_dotenv

load_dotenv()

async def run_ocr(image_data: bytes) -> tuple[str, dict, float]:
    # Lấy API Key từ .env
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
    try:
        # Truyền api_key trực tiếp
        client = genai.Client(api_key=api_key)
        # Mở ảnh từ dữ liệu bytes truyền vào
        img = Image.open(io.BytesIO(image_data))
        
        prompt = """
        Extract business card information.
        Return a JSON object with the following keys:
        - full_name
        - company
        - position
        - emails (list of strings)
        - phones (list of strings)
        - website
        - address
        - confidence (a float between 0 and 1 representing your confidence in the extraction)
        """
        
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        # Gemini trả về JSON sạch khi dùng response_mime_type
        raw_text = response.text.strip()
        extracted_data = json.loads(raw_text)
        
        # Lấy độ tin cậy từ Gemini trả về, mặc định là 0.0 nếu không có
        confidence = extracted_data.get("confidence", 0.0)
        
        return raw_text, extracted_data, confidence
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise

async def save_scan(
    image_url: str,
    raw_text: str,
    extracted_data: dict,
    confidence_score: float,
    contact_id: str | None = None,
) -> dict:
    db = await get_db()
    stored_contact_id = None
    if contact_id:
        try:
            stored_contact_id = ObjectId(contact_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid contact ID")
    doc = BusinessCardScanDocument(
        contact_id=contact_id,
        image_url=image_url,
        raw_text=raw_text,
        extracted_data=extracted_data,
        confidence_score=confidence_score,
        status=STATUS_DONE,
    )
    scan_data = doc.model_dump(mode="json", exclude_none=True)
    if stored_contact_id:
        scan_data["contact_id"] = stored_contact_id
    result = await db[COLLECTION].insert_one(scan_data)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return jsonable_encoder(created, custom_encoder={ObjectId: str})
