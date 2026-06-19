from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from ...core.database import get_db
from .models import TagDocument
from .schemas import TagCreate, TagUpdate

COLLECTION = "tags"


def _encode(doc):
    return jsonable_encoder(doc, custom_encoder={ObjectId: str})


def _object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid tag ID")


def _raise_not_found() -> None:
    raise HTTPException(status_code=404, detail="Tag not found")


async def create(data: TagCreate) -> dict:
    db = await get_db()
    doc = TagDocument(**data.model_dump())
    result = await db[COLLECTION].insert_one(doc.model_dump(mode="json", exclude_none=True))
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _encode(created)


async def list_tags() -> list:
    db = await get_db()
    docs = await db[COLLECTION].find({}).to_list(length=200)
    return _encode(docs)


async def get(tag_id: str) -> dict:
    db = await get_db()
    doc = await db[COLLECTION].find_one({"_id": _object_id(tag_id)})
    if not doc:
        _raise_not_found()
    return _encode(doc)


async def update(tag_id: str, data: TagUpdate) -> dict:
    db = await get_db()
    tag_object_id = _object_id(tag_id)
    existing = await db[COLLECTION].find_one({"_id": tag_object_id})
    if not existing:
        _raise_not_found()

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        return _encode(existing)
    doc = await db[COLLECTION].find_one_and_update(
        {"_id": tag_object_id},
        {"$set": update_data},
        return_document=True,
    )
    return _encode(doc)


async def delete(tag_id: str) -> None:
    db = await get_db()
    tag_object_id = _object_id(tag_id)
    existing = await db[COLLECTION].find_one({"_id": tag_object_id})
    if not existing:
        _raise_not_found()
    await db[COLLECTION].delete_one({"_id": tag_object_id})
