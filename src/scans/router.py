from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from ..auth.dependencies import get_current_user_id
from .dependencies import validate_image_file
from .schemas import ScanResponse
from . import service
from ..storage.service import StorageService
from ..contacts import service as contact_service
from ..contacts.schemas import ContactCreate

import asyncio

router = APIRouter(prefix="/scans", tags=["scans"])
storage_service = StorageService()

@router.post("/upload", response_model=ScanResponse, status_code=201)
async def upload_scan(
    file: UploadFile = Depends(validate_image_file),
    user_id: str = Depends(get_current_user_id),
):
    """
    Upload a business card image, extract data using AI, and automatically create a contact.
    """
    try:
        # Read image data
        image_data = await file.read()
        
        # 1. Optimization: Run Storage upload and OCR in parallel to reduce total API response time
        upload_task = storage_service.upload_file(
            image_data, user_id, file.filename, file.content_type
        )
        ocr_task = service.run_ocr(image_data)
        
        # Wait for both tasks to complete
        image_url, (raw_text, extracted_data, confidence_score) = await asyncio.gather(
            upload_task, ocr_task
        )

        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image to storage")
        if not extracted_data:
            raise HTTPException(status_code=422, detail="Failed to extract data from image")
        
    except Exception as e:
        # catch any unexpected errors during upload or OCR
        print(f"Error during upload or OCR: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to process image: {str(e)}"
        )

    try:
        # 2. Prepare data for Contact creation
        # Map data from Gemini (list) to Contact Schema (string)
        contact_in = ContactCreate(
            full_name=extracted_data.get("full_name") or "Unknown",
            company=extracted_data.get("company"),
            position=extracted_data.get("position"),
            email=extracted_data.get("emails")[0] if extracted_data.get("emails") else None,
            phone=extracted_data.get("phones")[0] if extracted_data.get("phones") else None,
            website=extracted_data.get("website"),
            address=extracted_data.get("address"),
            source_note="Scanned from business card"
        )
        
        # 3. Create Contact in DB
        contact = await contact_service.create(contact_in, user_id)
        contact_id = contact.get("id") or contact.get("_id")

        # 4. Save scan history to DB
        scan_record = await service.save_scan(
            image_url=image_url,
            raw_text=raw_text,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            contact_id=str(contact_id)
        )

        # 5. Return the result
        return scan_record

    except NotImplementedError:
        raise HTTPException(status_code=501, detail="OCR feature is not implemented yet")
    except Exception as e:
        print(f"Error saving scan data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error occurred while saving results: {str(e)}"
        )