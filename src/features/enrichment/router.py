from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import get_current_user_id
from .schemas import EnrichmentResultCreate, EnrichmentResultResponse, EnrichmentResultUpdate
from . import service

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


@router.post("", response_model=EnrichmentResultResponse, status_code=201)
async def create_enrichment_result(data: EnrichmentResultCreate, user_id: str = Depends(get_current_user_id)):
    return await service.create(data, user_id)


@router.get("/contacts/{contact_id}", response_model=EnrichmentResultResponse)
async def get_enrichment_result(contact_id: str, user_id: str = Depends(get_current_user_id)):
    result = await service.get_by_contact(contact_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Enrichment result not found")
    return result


@router.put("/contacts/{contact_id}", response_model=EnrichmentResultResponse)
async def update_enrichment_result(
    contact_id: str,
    data: EnrichmentResultUpdate,
    user_id: str = Depends(get_current_user_id),
):
    result = await service.update_by_contact(contact_id, user_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Enrichment result not found")
    return result


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_enrichment_result(contact_id: str, user_id: str = Depends(get_current_user_id)):
    deleted = await service.delete_by_contact(contact_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Enrichment result not found")
