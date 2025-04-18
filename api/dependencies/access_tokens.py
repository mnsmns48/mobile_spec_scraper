from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from database.engine import db
from database.models import User, AccessToken

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_token_db(session: Annotated["AsyncSession", Depends(db.scoped_session)]):
    yield AccessToken.get_db(session=session)
