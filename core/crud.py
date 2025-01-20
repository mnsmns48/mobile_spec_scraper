from typing import Any, Sequence
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.decl_api import DeclarativeBase


async def write_data(session: AsyncSession,
                     table: type[DeclarativeBase],
                     data: list | dict) -> None:
    await session.execute(insert(table).values(data))
    await session.commit()


async def get_data(session: AsyncSession,
                   table: type[DeclarativeBase],
                   conditions: dict[str, Any] = None) -> Sequence[DeclarativeBase]:
    stmt = select(table)
    if conditions:
        where_conditions = list()
        for column, value in conditions.items():
            column = getattr(table, column)
            where_conditions.append(column == value)
        stmt = stmt.where(and_(*where_conditions))
    result = await session.execute(stmt)
    return result.scalars().all()
