from fastapi_users import schemas
from pydantic import BaseModel

from config.settings import var_types


class UserRead(schemas.BaseUser[var_types.UserIdType]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


# class UserRegisteredNotification(BaseModel):
#     user: UserRead
#     ts: int
