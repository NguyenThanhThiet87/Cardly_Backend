from fastapi import Depends
from ..auth.dependencies import get_current_user_id
from .service import get
from .exceptions import ContactAccessDenied


async def get_contact_or_404(contact_id: str) -> dict:
    return await get(contact_id)


async def verify_contact_owner(
    contact: dict = Depends(get_contact_or_404),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    if str(contact["owner_id"]) != user_id:
        raise ContactAccessDenied()
    return contact
