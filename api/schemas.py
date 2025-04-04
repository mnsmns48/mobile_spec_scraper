from typing import Optional, List

from fastapi import Form
from pydantic import BaseModel


class Info(BaseModel):
    title: str


class Link(BaseModel):
    url: str
    title: Optional[str | None]
    source: Optional[str | None]


class ItemList(BaseModel):
    items: List[str]


def take_form_result(url: str = Form(...),
                     title: str = Form('string'),
                     source: str = Form('string')
                     ):
    return Link(url=url, title=title, source=source)
