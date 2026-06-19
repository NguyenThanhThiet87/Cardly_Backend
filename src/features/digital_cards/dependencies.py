from .service import  get_digital_card_service
from fastapi import Depends
from ..auth.dependencies import get_current_user_id

async def validate_owner_digital_card(digital_card_id: str, user_id = Depends(get_current_user_id)):
    digital_card = await get_digital_card_service(digital_card_id)
    return str(digital_card["owner_id"]) == user_id
