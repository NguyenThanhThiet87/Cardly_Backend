from fastapi import Depends
from src.auth.dependencies import get_current_user_id
from .service import get_me
from .exceptions import UserNotFound


async def get_user_or_404(user_id: str = Depends(get_current_user_id)) -> dict:
    user = await get_me(user_id)
    if not user:
        raise UserNotFound()
    return user
