import re


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0") and len(digits) == 10:
        return "+84" + digits[1:]
    return digits


def build_contact_filter_query(owner_id: str, tag: str | None, search: str | None) -> dict:
    query: dict = {"owner_id": owner_id}
    if tag:
        query["tag_ids"] = tag
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
        ]
    return query
