from asyncio import current_task
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator


import asyncpg
from pydantic_settings import BaseSettings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session, AsyncSession

from config import db_conf, logger


class Settings(BaseSettings):
    db_url: str = (f"postgresql+asyncpg://{db_conf.db_username}:{db_conf.db_password}"
                   f"@{db_conf.db_host}:{db_conf.db_port}/{db_conf.database}")
    db_echo: bool = False


settings = Settings()


class DataBase:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url,
                                          echo=echo,
                                          poolclass=NullPool)
        self.session_factory = async_sessionmaker(bind=self.engine,
                                                  autoflush=False,
                                                  autocommit=False,
                                                  expire_on_commit=False)

    @asynccontextmanager
    async def scoped_session(self) -> AsyncGenerator[AsyncSession | Any, Any]:
        session = async_scoped_session(session_factory=self.session_factory, scopefunc=current_task)
        try:
            async with session() as sess:
                yield sess
        finally:
            await session.remove()


db = DataBase(settings.db_url, settings.db_echo)


async def create_db():
    conn = await asyncpg.connect(database='postgres',
                                 user=db_conf.db_username,
                                 password=db_conf.db_password,
                                 host=db_conf.db_host,
                                 port=db_conf.db_port
                                 )
    sql = f'CREATE DATABASE {db_conf.database}'
    await conn.execute(sql)
    await conn.close()
    logger.info(f"Database {db_conf.database} success created")