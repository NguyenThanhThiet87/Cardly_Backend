from database import get_db
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from .schemas import ContactCreate, ContactUpdate
from .models import ContactDocument
from .utils import build_contact_filter_query

COLLECTION = "contacts"


def _encode(doc: dict) -> dict:
    return jsonable_encoder(doc, custom_encoder={ObjectId: str})


async def create(data: ContactCreate, owner_id: str) -> dict:
    db = await get_db()
    doc = ContactDocument(**data.model_dump(), owner_id=owner_id)
    result = await db[COLLECTION].insert_one(doc.model_dump(mode="json", exclude_none=True))
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _encode(created)


async def get(contact_id: str) -> dict | None:
    try:
        db = await get_db()
        doc = await db[COLLECTION].find_one({"_id": ObjectId(contact_id)})
        return _encode(doc) if doc else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid contact ID")


async def list_contacts(owner_id: str, tag: str | None = None, search: str | None = None) -> list:
    db = await get_db()
    query = build_contact_filter_query(owner_id, tag, search)
    docs = await db[COLLECTION].find(query).to_list(length=200)
    return _encode(docs)


async def update(contact_id: str, data: ContactUpdate) -> dict | None:
    try:
        db = await get_db()
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)
        doc = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(contact_id)},
            {"$set": update_data},
            return_document=True,
        )
        return _encode(doc) if doc else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid contact ID")


async def delete(contact_id: str) -> bool:
    try:
        db = await get_db()
        result = await db[COLLECTION].delete_one({"_id": ObjectId(contact_id)})
        return result.deleted_count > 0
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid contact ID")


async def toggle_favorite(contact_id: str, value: bool) -> dict | None:
    try:
        db = await get_db()
        doc = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(contact_id)},
            {"$set": {"is_favorite": value, "updated_at": datetime.now(timezone.utc)}},
            return_document=True,
        )
        return _encode(doc) if doc else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid contact ID")
