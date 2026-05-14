from fastapi import HTTPException
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from database import connect_to_mongo
from .schemas import DigitalCardCreate, DigitalCardUpdate
from .models import DigitalCardModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_db
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument


COLLECTION_NAME = "digital_cards"

async def get_digital_cards_service():
    try:
        db = await get_db()
        collection = db[COLLECTION_NAME]
        cards = await collection.find({"is_public": True}).to_list(length=100)
        return jsonable_encoder(cards, custom_encoder={ObjectId: str})
    except Exception as e:
        raise e

async def get_digital_card_service(digital_card_id: str):
    try:
        db = await get_db()
        collection = db[COLLECTION_NAME]
        card = await collection.find_one({"_id": ObjectId(digital_card_id)})
        return jsonable_encoder(card, custom_encoder={ObjectId: str})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")
    except Exception as e:
        raise e

async def create_digital_card_service(card_in: DigitalCardCreate, owner_id: str):
    try:
        db = await get_db()
        collection = db[COLLECTION_NAME]
        
        # Convert client payload to DB model, enforcing owner_id from token
        db_card = DigitalCardModel(**card_in.model_dump(), owner_id=owner_id)
        card_data = db_card.model_dump(mode='json', exclude_none=True)

        result = await collection.insert_one(card_data)
        return {"message": "Digital card created successfully"+f" with id {result.inserted_id}"}
    except Exception as e:
        raise e

async def update_digital_card_service(digital_card_id: str, card_in: DigitalCardUpdate):
    try:
        db = await get_db()
        collection = db[COLLECTION_NAME]
        
        # Extract only the fields the client wants to update (excluding None/Unset values)
        update_data = card_in.model_dump(mode='json', exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            result = await collection.update_one({"_id": ObjectId(digital_card_id) }, {"$set": update_data})
            return result.matched_count > 0
        return False
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")
    except Exception as e:
        raise e

async def toggle_public_digital_card_service(digital_card_id: str, is_public: bool):
    try:
        db = await get_db()
        collection = db[COLLECTION_NAME]
        # Use find_one_and_update to apply changes and return the LATEST document
        updated_card = await collection.find_one_and_update(
            {"_id": ObjectId(digital_card_id)}, 
            {"$set": {"is_public": is_public, "updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER
        )
        
        if updated_card:
            return jsonable_encoder(updated_card, custom_encoder={ObjectId: str})
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid digital card ID")
    except Exception as e:
        raise e
