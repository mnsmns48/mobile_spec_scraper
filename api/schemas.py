from typing import Optional

from pydantic import BaseModel


class Info(BaseModel):
    title: str
    brand: str
    product_type: Optional[str | None]


# class DeviceSchema(BaseModel):
#     id: int
#     title: str
#     brand: str
#     product_type: Optional[str] = None
#     link: str
#     source: str
#     info: dict
#     pros_cons: Optional[dict] = None
#     create: datetime
#     update: datetime
#     model_config = ConfigDict(from_attributes=True)
