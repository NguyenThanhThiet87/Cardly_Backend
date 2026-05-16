import re
from bson import ObjectId
from bson.errors import InvalidId


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0") and len(digits) == 10:
        return "+84" + digits[1:]
    return digits


def build_contact_filter_query(owner_id: str, tag: str | None, search: str | None) -> dict:
    owner_values: list = [owner_id]
    try:
        owner_values.append(ObjectId(owner_id))
    except InvalidId:
        pass
    query: dict = {"owner_id": {"$in": owner_values}}
    if tag:
        tag_values: list = [tag]
        try:
            tag_values.append(ObjectId(tag))
        except InvalidId:
            pass
        query["tag_ids"] = {"$in": tag_values}
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
        ]
    return query
