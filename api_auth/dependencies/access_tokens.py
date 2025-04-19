from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from database.engine import db
from database.models import AccessToken

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_token_db(session: Annotated["AsyncSession", Depends(db.session_getter)]):
    yield AccessToken.get_db(session=session)
