from src.database import get_db
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


def _with_list_fields(doc: dict | None) -> dict | None:
    if not doc:
        return doc
    for field in ("email", "phone"):
        if isinstance(doc.get(field), str):
            doc[field] = [doc[field]]
    return doc


def _to_object_id(value: str, field_name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _normalize_contact_doc(doc: dict) -> dict:
    if "owner_id" in doc:
        doc["owner_id"] = _to_object_id(doc["owner_id"], "owner ID")
    if "tag_ids" in doc:
        doc["tag_ids"] = [_to_object_id(tag_id, "tag ID") for tag_id in doc.get("tag_ids", [])]
    return doc


async def create(data: ContactCreate, owner_id: str) -> dict:
    db = await get_db()
    doc = ContactDocument(**data.model_dump(), owner_id=owner_id)
    contact_data = _normalize_contact_doc(doc.model_dump(mode="json", exclude_none=True))
    result = await db[COLLECTION].insert_one(contact_data)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _encode(created)


async def get(contact_id: str) -> dict | None:
    try:
        db = await get_db()
        doc = await db[COLLECTION].find_one({"_id": ObjectId(contact_id)})
        doc = _with_list_fields(doc)
        return _encode(doc) if doc else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid contact ID")


async def list_contacts(owner_id: str, tag: str | None = None, search: str | None = None) -> list:
    db = await get_db()
    query = build_contact_filter_query(owner_id, tag, search)
    docs = await db[COLLECTION].find(query).to_list(length=200)
    docs = [_with_list_fields(doc) for doc in docs]
    return _encode(docs)


async def update(contact_id: str, data: ContactUpdate) -> dict | None:
    try:
        db = await get_db()
        update_data = data.model_dump(mode="json", exclude_none=True)
        if "tag_ids" in update_data:
            update_data["tag_ids"] = [_to_object_id(tag_id, "tag ID") for tag_id in update_data["tag_ids"]]
        update_data["updated_at"] = datetime.now(timezone.utc)
        doc = await db[COLLECTION].find_one_and_update(
            {"_id": ObjectId(contact_id)},
            {"$set": update_data},
            return_document=True,
        )
        doc = _with_list_fields(doc)
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
        doc = _with_list_fields(doc)
        return _encode(doc) if doc else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid contact ID")
