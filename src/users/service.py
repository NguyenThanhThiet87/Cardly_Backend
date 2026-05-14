from database import get_db
from bson import ObjectId
from datetime import datetime, timezone
from .schemas import UserUpdate
from .utils import build_user_response

COLLECTION = "users"


async def get_me(user_id: str) -> dict | None:
    db = await get_db()
    user = await db[COLLECTION].find_one({"_id": ObjectId(user_id)})
    return build_user_response(user) if user else None


async def update_profile(user_id: str, data: UserUpdate) -> dict | None:
    db = await get_db()
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["updated_at"] = datetime.now(timezone.utc)
    user = await db[COLLECTION].find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update},
        return_document=True,
    )
    return build_user_response(user) if user else None


async def delete_account(user_id: str) -> bool:
    db = await get_db()
    result = await db[COLLECTION].delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0
