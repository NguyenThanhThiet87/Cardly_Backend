from .schemas import ExtractedCardData

from ...core.database import get_db
import os
import asyncio
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from .models import BusinessCardScanDocument
from .utils import extract_text_fields
from .constants import STATUS_DONE, STATUS_FAILED

from ..storage.service import StorageService
from ..contacts import service as contact_service
from ..contacts.schemas import ContactCreate
from ..enrichment import service as enrichment_service
from ..enrichment.schemas import EnrichmentResultCreate

COLLECTION = "business_card_scans"

import io
import json
from google import genai
from PIL import Image

from google.genai import types
from google.genai.types import Tool, GenerateContentConfig

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
        confidence (a float between 0 and 1 representing your confidence in the extraction)
        """
        
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[prompt, img],
            config= GenerateContentConfig(
                response_mime_type="application/json",
                response_schema = ExtractedCardData.model_json_schema(),
                tools=[
                   {"url_context": {}},
                ],
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


async def process_scan_and_enrich(
    image_data: bytes,
    filename: str,
    content_type: str,
    user_id: str
) -> dict:
    """
    Tải ảnh lên Storage, chạy OCR trích xuất thông tin, tự động tạo Contact
    và thực hiện Enrichment nếu có website.
    """
    try:
        storage_service = StorageService()
        
        # 1. Chạy song song tải ảnh lên storage và OCR bằng Gemini
        upload_task = storage_service.upload_file(
            image_data, user_id, filename, content_type
        )
        ocr_task = run_ocr(image_data)
        
        image_url, (raw_text, extracted_data, confidence_score) = await asyncio.gather(
            upload_task, ocr_task
        )
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image to storage")
        if not extracted_data:
            raise HTTPException(status_code=422, detail="Failed to extract data from image")
            
    except Exception as e:
        print(f"Error during upload or OCR: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to process image: {str(e)}"
        )
        
    try:
        # 2. Tạo Contact từ thông tin trích xuất
        contact_in = ContactCreate(
            full_name=extracted_data.get("full_name") or "Unknown",
            company=extracted_data.get("company"),
            position=extracted_data.get("position"),
            emails=extracted_data.get("emails") or [],
            phones=extracted_data.get("phones") or [],
            website=extracted_data.get("website"),
            address=extracted_data.get("address"),
            source_note="Scanned from business card"
        )
        
        contact = await contact_service.create(contact_in, user_id)
        contact_id = contact.get("id") or contact.get("_id")
        
        # 3. Tích hợp Enrichment tự động nếu danh thiếp có website
        if contact_in.website:
            try:
                # Gọi service làm giàu thông tin (Gemini) từ website
                enrich_data = await enrichment_service.enrich([contact_in.website])
                
                # Lưu thông tin làm giàu vào CSDL
                enrich_in = EnrichmentResultCreate(
                    contact_id=str(contact_id),
                    professional_brief=enrich_data.professional_brief,
                    keywords=enrich_data.keywords,
                    highlights=enrich_data.highlights
                )
                await enrichment_service.create(enrich_in, user_id)
            except Exception as enrich_err:
                # Log lỗi nhưng không làm gián đoạn luồng chính lưu danh thiếp
                print(f"Enrichment failed for website {contact_in.website}: {enrich_err}")
                
        # 4. Lưu lịch sử quét danh thiếp
        scan_record = await save_scan(
            image_url=image_url,
            raw_text=raw_text,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            contact_id=str(contact_id)
        )
        
        return scan_record
        
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="OCR feature is not implemented yet")
    except Exception as e:
        print(f"Error saving scan data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while saving results: {str(e)}"
        )

from pydantic import BaseModel, Field
from typing import Optional

class ExtractedField(BaseModel):
    value: Optional[str] = Field(None, description="The extracted text value from the driver's license.")
    confidence: float = Field(0.0, description="A float between 0.0 and 1.0 representing confidence in this field's extraction and accuracy against the image.")

class ConditionDescription(BaseModel):
    condition: Optional[str] = ""
    description: Optional[str] = ""

class DriverLicense(BaseModel):
    full_name: Optional[ExtractedField] = None
    date_of_birth: Optional[ExtractedField] = None
    licence_number: Optional[ExtractedField] = None
    expiry_date: Optional[ExtractedField] = None
    address: Optional[ExtractedField] = None
    licence_class: Optional[ExtractedField] = None
    conditions: Optional[ExtractedField] = None
    condition_descriptions: Optional[list[ConditionDescription]] = None
    state: Optional[ExtractedField] = None
    card_number: Optional[ExtractedField] = None
    issue_date: Optional[ExtractedField] = None
    confidence: float = Field(0.0, description="Overall average confidence score for the entire extraction between 0.0 and 1.0.")

async def run_ocr_multiple(images_data: list[bytes]) -> tuple[str, dict, float]:
    # Lấy API Key từ .env
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
    try:
        # Truyền api_key trực tiếp
        client = genai.Client(api_key=api_key)
        # Mở ảnh từ dữ liệu bytes truyền vào
        imgs = [Image.open(io.BytesIO(image_data)) for image_data in images_data]
        
        prompt = """
        Extract Australian driver license information.
        
        Rules:
        - Format dates as YYYY-MM-DD.
        - If a field is not present or cannot be read, set value to null and confidence to 0.0.
        - The "confidence" field at the root of the JSON should be the overall average confidence score.
        """
        
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[prompt] + imgs,
            config= GenerateContentConfig(
                response_mime_type="application/json",
                response_schema = DriverLicense.model_json_schema(),
                tools=[
                   {"url_context": {}},
                ],
            )
        )
        if response.usage_metadata:
            print(f"Token Usage: Prompt={response.usage_metadata.prompt_token_count}, "
                  f"Candidates={response.usage_metadata.candidates_token_count}, "
                  f"Total={response.usage_metadata.total_token_count}")
        
        # Gemini trả về JSON sạch khi dùng response_mime_type
        raw_text = response.text.strip()
        extracted_data = json.loads(raw_text)
        
        return extracted_data
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise