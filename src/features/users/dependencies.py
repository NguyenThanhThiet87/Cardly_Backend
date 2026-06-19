from fastapi import Depends
from ..auth.dependencies import get_current_user_id
from .service import get_me


async def get_user_or_404(user_id: str = Depends(get_current_user_id)) -> dict:
    return await get_me(user_id)
