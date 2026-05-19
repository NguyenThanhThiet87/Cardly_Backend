from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_user_id
from .schemas import TagCreate, TagResponse, TagUpdate
from . import service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(data: TagCreate, _: str = Depends(get_current_user_id)):
    return await service.create(data)


@router.get("", response_model=list[TagResponse])
async def list_tags(_: str = Depends(get_current_user_id)):
    return await service.list_tags()


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: str, _: str = Depends(get_current_user_id)):
    return await service.get(tag_id)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: str, data: TagUpdate, _: str = Depends(get_current_user_id)):
    return await service.update(tag_id, data)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: str, _: str = Depends(get_current_user_id)):
    await service.delete(tag_id)
