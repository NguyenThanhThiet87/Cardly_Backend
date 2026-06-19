from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from ...core.database import get_db
from .schemas import DigitalCardCreate, DigitalCardUpdate
from .models import DigitalCardModel
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument

COLLECTION_NAME = "digital_cards"


def _owner_query(owner_id: str) -> dict:
    try:
        return {"owner_id": {"$in": [owner_id, ObjectId(owner_id)]}}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID")


def _digital_card_not_found() -> None:
    raise HTTPException(status_code=404, detail="Digital card not found")


def _public_card_not_found() -> None:
    raise HTTPException(status_code=404, detail="Public card not found")


async def get_digital_cards_service(owner_id: str):
    db = await get_db()
    cards = await db[COLLECTION_NAME].find(_owner_query(owner_id)).to_list(length=100)
    return jsonable_encoder(cards, custom_encoder={ObjectId: str})


async def get_digital_card_service(digital_card_id: str, owner_id: str | None = None):
    try:
        db = await get_db()
        query = {"_id": ObjectId(digital_card_id)}
        if owner_id:
            query.update(_owner_query(owner_id))
        card = await db[COLLECTION_NAME].find_one(query)
        if not card:
            _digital_card_not_found()
        return jsonable_encoder(card, custom_encoder={ObjectId: str})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")


async def create_digital_card_service(card_in: DigitalCardCreate, owner_id: str):
    try:
        db = await get_db()
        db_card = DigitalCardModel(**card_in.model_dump(), owner_id=owner_id)
        card_data = db_card.model_dump(mode="json", exclude_none=True)
        card_data["owner_id"] = ObjectId(owner_id)
        result = await db[COLLECTION_NAME].insert_one(card_data)
        created = await db[COLLECTION_NAME].find_one({"_id": result.inserted_id})
        return jsonable_encoder(created, custom_encoder={ObjectId: str})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create digital card: {str(e)}")


async def update_digital_card_service(digital_card_id: str, card_in: DigitalCardUpdate):
    try:
        db = await get_db()
        card_object_id = ObjectId(digital_card_id)
        existing = await db[COLLECTION_NAME].find_one({"_id": card_object_id})
        if not existing:
            _digital_card_not_found()

        update_data = card_in.model_dump(mode="json", exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await db[COLLECTION_NAME].update_one({"_id": card_object_id}, {"$set": update_data})
        return True
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")


async def toggle_public_digital_card_service(digital_card_id: str, is_public: bool):
    try:
        db = await get_db()
        card_object_id = ObjectId(digital_card_id)
        existing = await db[COLLECTION_NAME].find_one({"_id": card_object_id})
        if not existing:
            _digital_card_not_found()

        updated_card = await db[COLLECTION_NAME].find_one_and_update(
            {"_id": card_object_id},
            {"$set": {"is_public": is_public, "updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return jsonable_encoder(updated_card, custom_encoder={ObjectId: str})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")


async def get_public_card_by_username_service(username: str):
    db = await get_db()
    # Join với users để tìm theo username, sau đó lấy card public của user đó
    user = await db["users"].find_one({"username": username})
    if not user:
        _public_card_not_found()
    owner_values = [str(user["_id"]), user["_id"]]
    card = await db[COLLECTION_NAME].find_one(
        {"owner_id": {"$in": owner_values}, "is_public": True}
    )
    if not card:
        _public_card_not_found()
    return jsonable_encoder(card, custom_encoder={ObjectId: str})
