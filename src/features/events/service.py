from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from ...core.database import get_db
from .models import EventDocument
from .schemas import EventCreate, EventUpdate

COLLECTION = "events"


def _encode(doc):
    return jsonable_encoder(doc, custom_encoder={ObjectId: str})


def _object_id(value: str, name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {name}")


def _owner_query(owner_id: str) -> dict:
    return {"owner_id": {"$in": [owner_id, _object_id(owner_id, "owner ID")]}}


def _normalize_ids(data: dict) -> dict:
    if "owner_id" in data:
        data["owner_id"] = _object_id(data["owner_id"], "owner ID")
    if "contact_ids" in data:
        data["contact_ids"] = [_object_id(contact_id, "contact ID") for contact_id in data["contact_ids"]]
    return data


async def create(data: EventCreate, owner_id: str) -> dict:
    db = await get_db()
    doc = EventDocument(**data.model_dump(), owner_id=owner_id)
    event_data = _normalize_ids(doc.model_dump(mode="json", exclude_none=True))
    result = await db[COLLECTION].insert_one(event_data)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _encode(created)


async def list_events(owner_id: str) -> list:
    db = await get_db()
    docs = await db[COLLECTION].find(_owner_query(owner_id)).to_list(length=200)
    return _encode(docs)


async def get(event_id: str, owner_id: str) -> dict | None:
    db = await get_db()
    doc = await db[COLLECTION].find_one({"_id": _object_id(event_id, "event ID"), **_owner_query(owner_id)})
    return _encode(doc) if doc else None


async def update(event_id: str, owner_id: str, data: EventUpdate) -> dict | None:
    db = await get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "contact_ids" in update_data:
        update_data["contact_ids"] = [_object_id(contact_id, "contact ID") for contact_id in update_data["contact_ids"]]
    if not update_data:
        return await get(event_id, owner_id)
    doc = await db[COLLECTION].find_one_and_update(
        {"_id": _object_id(event_id, "event ID"), **_owner_query(owner_id)},
        {"$set": update_data},
        return_document=True,
    )
    return _encode(doc) if doc else None


async def delete(event_id: str, owner_id: str) -> bool:
    db = await get_db()
    result = await db[COLLECTION].delete_one({"_id": _object_id(event_id, "event ID"), **_owner_query(owner_id)})
    return result.deleted_count > 0
