from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import (SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase)
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import var_types
from ._mixins import IdIntPkMixin
from .base import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(Base, IdIntPkMixin, SQLAlchemyBaseUserTable[var_types.UserIdType]):
    telegram_id: Mapped[int] = mapped_column(nullable=True)

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)
