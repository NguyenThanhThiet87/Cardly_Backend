from ...core.database import get_db
from bson import ObjectId
from datetime import datetime, timezone
from .schemas import UserUpdate
from .utils import build_user_response

COLLECTION = "users"


def _raise_not_found() -> None:
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="User not found")


async def get_me(user_id: str) -> dict:
    from bson.errors import InvalidId
    from fastapi import HTTPException
    try:
        db = await get_db()
        user = await db[COLLECTION].find_one({"_id": ObjectId(user_id)})
        if not user:
            _raise_not_found()
        return build_user_response(user)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID")


async def update_profile(user_id: str, data: UserUpdate) -> dict:
    from bson.errors import InvalidId
    from fastapi import HTTPException
    try:
        db = await get_db()
        user_object_id = ObjectId(user_id)
        existing = await db[COLLECTION].find_one({"_id": user_object_id})
        if not existing:
            _raise_not_found()

        update = {k: v for k, v in data.model_dump().items() if v is not None}
        update["updated_at"] = datetime.now(timezone.utc)
        user = await db[COLLECTION].find_one_and_update(
            {"_id": user_object_id},
            {"$set": update},
            return_document=True,
        )
        return build_user_response(user)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID")


async def delete_account(user_id: str) -> None:
    from bson.errors import InvalidId
    from fastapi import HTTPException
    try:
        db = await get_db()
        user_object_id = ObjectId(user_id)
        existing = await db[COLLECTION].find_one({"_id": user_object_id})
        if not existing:
            _raise_not_found()
        await db[COLLECTION].delete_one({"_id": user_object_id})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID")
