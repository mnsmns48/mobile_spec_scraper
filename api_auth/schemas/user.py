from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel

from config.settings import var_types


class UserRead(schemas.BaseUser[var_types.UserIdType]):
    telegram_id: Optional[int]


class UserCreate(schemas.BaseUserCreate):
    telegram_id: Optional[int]


class UserUpdate(schemas.BaseUserUpdate):
    telegram_id: Optional[int]

# class UserRegisteredNotification(BaseModel):
#     user: UserRead
#     ts: int
