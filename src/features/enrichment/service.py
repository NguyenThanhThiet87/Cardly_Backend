from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from ...core.database import get_db
from ...features.contacts.service import get as get_contact
from .models import EnrichmentResultDocument
from .schemas import EnrichmentResultCreate, EnrichmentResultUpdate

COLLECTION = "enrichment_results"


def _encode(doc):
    return jsonable_encoder(doc, custom_encoder={ObjectId: str})


def _object_id(value: str, name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {name}")


def _raise_not_found() -> None:
    raise HTTPException(status_code=404, detail="Enrichment result not found")


async def _ensure_contact_owner(contact_id: str, owner_id: str) -> None:
    contact = await get_contact(contact_id)
    if str(contact["owner_id"]) != owner_id:
        raise HTTPException(status_code=403, detail="Access denied")


async def create(data: EnrichmentResultCreate, owner_id: str) -> dict:
    await _ensure_contact_owner(data.contact_id, owner_id)
    db = await get_db()
    doc = EnrichmentResultDocument(**data.model_dump())
    result_data = doc.model_dump(mode="json", exclude_none=True)
    result_data["contact_id"] = _object_id(data.contact_id, "contact ID")
    result = await db[COLLECTION].insert_one(result_data)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _encode(created)


async def get_by_contact(contact_id: str, owner_id: str) -> dict:
    await _ensure_contact_owner(contact_id, owner_id)
    db = await get_db()
    doc = await db[COLLECTION].find_one({"contact_id": {"$in": [contact_id, _object_id(contact_id, "contact ID")]}})
    if not doc:
        _raise_not_found()
    return _encode(doc)


async def update_by_contact(contact_id: str, owner_id: str, data: EnrichmentResultUpdate) -> dict:
    await _ensure_contact_owner(contact_id, owner_id)
    db = await get_db()
    contact_query = {"contact_id": {"$in": [contact_id, _object_id(contact_id, "contact ID")]}}
    existing = await db[COLLECTION].find_one(contact_query)
    if not existing:
        _raise_not_found()

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    doc = await db[COLLECTION].find_one_and_update(
        contact_query,
        {"$set": update_data},
        return_document=True,
    )
    return _encode(doc)


async def delete_by_contact(contact_id: str, owner_id: str) -> None:
    await _ensure_contact_owner(contact_id, owner_id)
    db = await get_db()
    contact_query = {"contact_id": {"$in": [contact_id, _object_id(contact_id, "contact ID")]}}
    existing = await db[COLLECTION].find_one(contact_query)
    if not existing:
        _raise_not_found()
    await db[COLLECTION].delete_one(contact_query)
