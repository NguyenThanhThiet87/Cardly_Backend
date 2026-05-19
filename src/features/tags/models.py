from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    color: str

    model_config = ConfigDict(populate_by_name=True)
