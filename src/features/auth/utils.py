from datetime import datetime
from .schemas import UserResponse


def build_user_response(user: dict) -> UserResponse:
    """Build a user response from a user document"""
    if not user:
        return None
    return UserResponse(
        id=str(user.get("_id")),
        email=user.get("email"),
        full_name=user.get("full_name"),
        username=user.get("username"),
        avatar_url=user.get("avatar_url"),
        is_active=user.get("is_active", True),
        created_at=user.get("created_at").isoformat() if user.get("created_at") else None
    )


def format_user_doc(user_doc: dict) -> dict:
    """Format user document for API response"""
    return {
        "id": str(user_doc.get("_id")),
        "email": user_doc.get("email"),
        "full_name": user_doc.get("full_name"),
        "username": user_doc.get("username"),
        "avatar_url": user_doc.get("avatar_url"),
        "is_active": user_doc.get("is_active", True),
        "created_at": user_doc.get("created_at").isoformat() if isinstance(user_doc.get("created_at"), datetime) else user_doc.get("created_at")
    }
