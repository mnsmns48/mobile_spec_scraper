from typing import List

from pydantic import BaseModel


class ItemList(BaseModel):
    items: List[str]