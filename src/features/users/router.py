from fastapi import APIRouter, Depends
from ..auth.dependencies import get_current_user_id
from .dependencies import get_user_or_404
from .schemas import UserResponse, UserUpdate
from .service import update_profile, delete_account

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me_route(user: dict = Depends(get_user_or_404)):
    return user


@router.put("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, user_id: str = Depends(get_current_user_id)):
    return await update_profile(user_id, data)


@router.delete("/me", status_code=204)
async def delete_me(user_id: str = Depends(get_current_user_id)):
    await delete_account(user_id)
