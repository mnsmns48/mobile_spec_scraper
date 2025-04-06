from datetime import datetime
from typing import Any, Sequence, Coroutine
from sqlalchemy import select, and_, Row
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.decl_api import DeclarativeBase

from core.utils import dt_to_minute_round
from database.models import Product, Brand


async def write_data(session: AsyncSession,
                     table: type[Product],
                     data: list | dict):
    stmt = insert(table).values(data)
    new_data = {
        'info': stmt.excluded.info,
        'pros_cons': stmt.excluded.pros_cons,
        'update': datetime.now()
    }
    new_stmt = stmt.on_conflict_do_update(
        constraint='uix_link',
        set_=new_data
    ).returning(table.create)
    result = await session.execute(new_stmt)
    await session.commit()
    row = result.fetchone()
    current_t = await dt_to_minute_round(datetime.now())
    row_create_t = await dt_to_minute_round(row.create)
    if current_t == row_create_t:
        return 'inserted'
    return 'updated'


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


async def add_new_brand(session: AsyncSession, title: str) -> Brand:
    brand = title.split(' ')[0].lower()
    stmt = insert(Brand).values({'brand': brand, 'brand_depends': [brand]}).returning(Brand)
    result = await session.execute(stmt)
    await session.commit()
    returning_brand = result.fetchone()
    return returning_brand[0]