from fastapi import APIRouter, Depends, UploadFile, HTTPException
from ..auth.dependencies import get_current_user_id
from .dependencies import validate_image_file
from .schemas import ScanResponse
from .utils import extract_text_fields
from . import service
from ..storage.service import StorageService

router = APIRouter(prefix="/scans", tags=["scans"])
storage_service = StorageService()

@router.post("/upload", response_model=ScanResponse, status_code=201)
async def upload_scan(
    file: UploadFile = Depends(validate_image_file),
    user_id: str = Depends(get_current_user_id),
):
    try:
        image_data = await file.read()
        # TODO: upload image_data to storage and get image_url
        image_url = await storage_service.upload_file(image_data, user_id, file.filename, file.content_type)

        raw_text, extracted_data, confidence_score = await service.run_ocr(image_data)
      
        return await service.save_scan(
            image_url=image_url,
            raw_text=raw_text,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
        )
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="OCR feature is not implemented yet")