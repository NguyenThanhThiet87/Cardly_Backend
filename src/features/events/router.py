from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import get_current_user_id
from .schemas import EventCreate, EventResponse, EventUpdate
from . import service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(data: EventCreate, user_id: str = Depends(get_current_user_id)):
    return await service.create(data, user_id)


@router.get("", response_model=list[EventResponse])
async def list_events(user_id: str = Depends(get_current_user_id)):
    return await service.list_events(user_id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, user_id: str = Depends(get_current_user_id)):
    event = await service.get(event_id, user_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, data: EventUpdate, user_id: str = Depends(get_current_user_id)):
    event = await service.update(event_id, user_id, data)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str, user_id: str = Depends(get_current_user_id)):
    deleted = await service.delete(event_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
