from typing import List

from pydantic import BaseModel


class ItemList(BaseModel):
    items: List[str]


class ItemInfoRequest(BaseModel):
    title: str
    brand: str | None = None
    type: str | None = None
