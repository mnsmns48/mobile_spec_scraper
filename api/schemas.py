from typing import Optional, List

from fastapi import Form
from pydantic import BaseModel
from pydantic_core import Url


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


class ItemList(BaseModel):
    items: List[str]


def take_form_result(url: str = Form(...),
                     title: str = Form('string'),
                     brand: str = Form('string'),
                     product_type: str = Form('string'),
                     source: str = Form('string')
                     ):
    return Link(url=url, title=title, brand=brand, product_type=product_type, source=source)
