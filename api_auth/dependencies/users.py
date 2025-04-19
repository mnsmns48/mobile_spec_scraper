from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from database.engine import db
from database.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(session: Annotated["AsyncSession", Depends(db.session_getter)]):
    yield User.get_db(session=session)
