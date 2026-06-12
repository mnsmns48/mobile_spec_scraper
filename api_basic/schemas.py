from typing import List

from pydantic import BaseModel


class ItemList(BaseModel):
    items: List[str]


class ItemInfoRequest(BaseModel):
    title: str
    brand: str | None = None
    type: str | None = None


class ProductResponse(BaseModel):
    title_line: str
    source: str
    pros_cons: dict
    info: list

    class Config:
        from_attributes = True
