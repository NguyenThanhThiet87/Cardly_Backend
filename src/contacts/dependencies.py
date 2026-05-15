from fastapi import Depends
from src.auth.dependencies import get_current_user_id
from .service import get
from .exceptions import ContactNotFound, ContactAccessDenied


async def get_contact_or_404(contact_id: str) -> dict:
    contact = await get(contact_id)
    if not contact:
        raise ContactNotFound()
    return contact


async def verify_contact_owner(
    contact: dict = Depends(get_contact_or_404),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    if str(contact["owner_id"]) != user_id:
        raise ContactAccessDenied()
    return contact
