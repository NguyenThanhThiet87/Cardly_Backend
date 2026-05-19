from .constants import DEFAULT_AVATAR_URL


def build_user_response(user: dict) -> dict:
    user["id"] = str(user.pop("_id"))
    if not user.get("avatar_url"):
        user["avatar_url"] = DEFAULT_AVATAR_URL
    user.pop("hashed_password", None)
    return user
