from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from database import get_db
from .schemas import DigitalCardCreate, DigitalCardUpdate
from .models import DigitalCardModel
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

COLLECTION_NAME = "digital_cards"


async def get_digital_cards_service():
    db = await get_db()
    cards = await db[COLLECTION_NAME].find({"is_public": True}).to_list(length=100)
    return jsonable_encoder(cards, custom_encoder={ObjectId: str})


async def get_digital_card_service(digital_card_id: str):
    try:
        db = await get_db()
        card = await db[COLLECTION_NAME].find_one({"_id": ObjectId(digital_card_id)})
        return jsonable_encoder(card, custom_encoder={ObjectId: str}) if card else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")


async def create_digital_card_service(card_in: DigitalCardCreate, owner_id: str):
    try:
        db = await get_db()
        db_card = DigitalCardModel(**card_in.model_dump(), owner_id=owner_id)
        card_data = db_card.model_dump(mode="json", exclude_none=True)
        result = await db[COLLECTION_NAME].insert_one(card_data)
        created = await db[COLLECTION_NAME].find_one({"_id": result.inserted_id})
        return jsonable_encoder(created, custom_encoder={ObjectId: str})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create digital card: {str(e)}")


async def update_digital_card_service(digital_card_id: str, card_in: DigitalCardUpdate):
    try:
        db = await get_db()
        update_data = card_in.model_dump(mode="json", exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            result = await db[COLLECTION_NAME].update_one(
                {"_id": ObjectId(digital_card_id)}, {"$set": update_data}
            )
            return result.matched_count > 0
        return False
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")


async def toggle_public_digital_card_service(digital_card_id: str, is_public: bool):
    try:
        db = await get_db()
        updated_card = await db[COLLECTION_NAME].find_one_and_update(
            {"_id": ObjectId(digital_card_id)},
            {"$set": {"is_public": is_public, "updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return jsonable_encoder(updated_card, custom_encoder={ObjectId: str}) if updated_card else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")


async def get_public_card_by_username_service(username: str):
    db = await get_db()
    # Join với users để tìm theo username, sau đó lấy card public của user đó
    user = await db["users"].find_one({"username": username})
    if not user:
        return None
    card = await db[COLLECTION_NAME].find_one(
        {"owner_id": str(user["_id"]), "is_public": True}
    )
    return jsonable_encoder(card, custom_encoder={ObjectId: str}) if card else None
