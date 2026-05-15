from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str
    color: str


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagCreate):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)
