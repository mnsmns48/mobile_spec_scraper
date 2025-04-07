from typing import List

from fastapi import Form
from pydantic import BaseModel


class Info(BaseModel):
    title: str


class Link(BaseModel):
    url: str


class ItemList(BaseModel):
    items: List[str]


def take_form_result(url: str = Form(...)):
    return Link(url=url)
