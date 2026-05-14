from fastapi import APIRouter, Depends, UploadFile
from src.auth.dependencies import get_current_user_id
from .dependencies import validate_image_file
from .schemas import ScanResponse
from .utils import extract_text_fields
from . import service

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/upload", response_model=ScanResponse, status_code=201)
async def upload_scan(
    file: UploadFile = Depends(validate_image_file),
    user_id: str = Depends(get_current_user_id),
):
    image_data = await file.read()
    # TODO: upload image_data to storage and get image_url
    image_url = f"https://storage.example.com/scans/{user_id}/{file.filename}"

    raw_text, confidence_score = await service.run_ocr(image_data)
    extracted_data = extract_text_fields(raw_text)

    return await service.save_scan(
        image_url=image_url,
        raw_text=raw_text,
        extracted_data=extracted_data,
        confidence_score=confidence_score,
    )
