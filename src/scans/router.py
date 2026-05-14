from fastapi import APIRouter, HTTPException, status, Depends
from .schemas import ScanResponse
from .service import scan_card_service

router = APIRouter()

@router.post("/scans", response_model=ScanResponse)
async def scan_business_card():
    return await scan_card_service()
