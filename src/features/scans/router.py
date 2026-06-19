from fastapi import APIRouter, Depends, UploadFile
from ..auth.dependencies import get_current_user_id
from .dependencies import validate_image_file
from .schemas import ScanResponse
from . import service

router = APIRouter(prefix="/scans", tags=["scans"])

@router.post("/upload", response_model=ScanResponse, status_code=201)
async def upload_scan(
    file: UploadFile = Depends(validate_image_file),
    user_id: str = Depends(get_current_user_id),
):
    """
    Upload a business card image, extract data using AI, automatically create a contact,
    and intelligently enrich the contact with company/professional data.
    """
    image_data = await file.read()
    return await service.process_scan_and_enrich(
        image_data=image_data,
        filename=file.filename,
        content_type=file.content_type,
        user_id=user_id
    )
