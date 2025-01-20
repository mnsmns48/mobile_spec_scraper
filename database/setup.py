import asyncio

from asyncpg import InvalidCatalogNameError

from database.engine import db, create_db
from database.models import Base


async def setup_db():
    try:
        async with db.engine.begin() as async_connect:
            await async_connect.run_sync(Base.metadata.create_all)
    except InvalidCatalogNameError:
        await asyncio.create_task(create_db())
        async with db.engine.begin() as async_connect:
            await async_connect.run_sync(Base.metadata.create_all)
