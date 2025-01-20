from typing import Optional

from pydantic import BaseModel


class Info(BaseModel):
    title: str
    brand: Optional[str | None]
    product_type: Optional[str | None]
    source: Optional[str | None]


class Link(BaseModel):
    url: str
    title: Optional[str | None]
    brand: Optional[str | None]
    product_type: Optional[str | None]
    source: Optional[str | None]