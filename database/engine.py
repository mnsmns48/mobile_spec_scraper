
from asyncio import current_task
from contextlib import asynccontextmanager

import asyncpg
from pydantic_settings import BaseSettings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session, AsyncSession

from config import hidden


class Settings(BaseSettings):
    db_url: str = (f"postgresql+asyncpg://{hidden.db_username}:{hidden.db_password}"
                   f"@localhost:{hidden.db_local_port}/{hidden.db_name}")
    db_echo: bool = False


settings = Settings()


class DataBase:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            poolclass=NullPool
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def scoped_session(self) -> AsyncSession:
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        try:
            async with session() as s:
                yield s
        finally:
            await session.remove()


db = DataBase(settings.db_url, settings.db_echo)


async def create_db():
    conn = await asyncpg.connect(database=hidden.old_db,
                                 user=hidden.db_username,
                                 password=hidden.db_password,
                                 host='localhost',
                                 port=hidden.db_local_port
                                 )
    sql = f'CREATE DATABASE "{hidden.db_name}"'
    await conn.execute(sql)
    await conn.close()
    print(f"DB <{hidden.db_name}> success created")