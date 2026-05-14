from fastapi import APIRouter, Depends
from typing import Optional
from src.auth.dependencies import get_current_user_id
from .dependencies import verify_contact_owner
from .schemas import ContactCreate, ContactUpdate, ContactResponse
from . import service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(data: ContactCreate, user_id: str = Depends(get_current_user_id)):
    return await service.create(data, user_id)


@router.get("", response_model=list[ContactResponse])
async def list_contacts(
    tag: Optional[str] = None,
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    return await service.list_contacts(user_id, tag, search)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact: dict = Depends(verify_contact_owner)):
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(data: ContactUpdate, contact: dict = Depends(verify_contact_owner)):
    return await service.update(contact["id"], data)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact: dict = Depends(verify_contact_owner)):
    await service.delete(contact["id"])


@router.patch("/{contact_id}/favorite", response_model=ContactResponse)
async def toggle_favorite(value: bool, contact: dict = Depends(verify_contact_owner)):
    return await service.toggle_favorite(contact["id"], value)
