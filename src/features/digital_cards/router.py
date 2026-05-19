from fastapi import APIRouter, HTTPException, status, Depends
from .schemas import DigitalCardResponse, DigitalCardCreate, DigitalCardUpdate
from .service import (
    get_digital_cards_service,
    get_digital_card_service,
    create_digital_card_service,
    update_digital_card_service,
    toggle_public_digital_card_service,
    get_public_card_by_username_service,
)
from ..auth.dependencies import get_current_user_id
from .dependencies import validate_owner_digital_card

router = APIRouter(tags=["digital-cards"])


@router.get("/digital-cards", response_model=list[DigitalCardResponse])
async def get_digital_cards(current_user_id: str = Depends(get_current_user_id)):
    return await get_digital_cards_service(current_user_id)


@router.post("/digital-cards", response_model=DigitalCardResponse, status_code=status.HTTP_201_CREATED)
async def create_digital_card(digital_card: DigitalCardCreate, current_user_id: str = Depends(get_current_user_id)):
    return await create_digital_card_service(digital_card, current_user_id)


@router.get("/digital-cards/{digital_card_id}", response_model=DigitalCardResponse)
async def get_digital_card(digital_card_id: str, current_user_id: str = Depends(get_current_user_id)):
    card = await get_digital_card_service(digital_card_id, current_user_id)
    if not card:
        raise HTTPException(status_code=404, detail="Digital card not found")
    return card


@router.put("/digital-cards/{digital_card_id}")
async def update_digital_card(digital_card_id: str, digital_card: DigitalCardUpdate, is_owner=Depends(validate_owner_digital_card)):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Forbidden")
    result = await update_digital_card_service(digital_card_id, digital_card)
    if not result:
        raise HTTPException(status_code=404, detail="Digital card not found")
    return {"message": "Digital card updated successfully"}


@router.patch("/digital-cards/{digital_card_id}/toggle-public", response_model=DigitalCardResponse)
async def toggle_public_digital_card(digital_card_id: str, is_public: bool, is_owner=Depends(validate_owner_digital_card)):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Forbidden")
    card = await toggle_public_digital_card_service(digital_card_id, is_public)
    if not card:
        raise HTTPException(status_code=404, detail="Digital card not found")
    return card


# Step 11: Public digital business card
@router.get("/public/{username}", response_model=DigitalCardResponse, tags=["public"])
async def get_public_card(username: str):
    card = await get_public_card_by_username_service(username)
    if not card:
        raise HTTPException(status_code=404, detail="Public card not found")
    return card
