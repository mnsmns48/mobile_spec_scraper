import re
from typing import Any
from sqlalchemy.orm import joinedload
from sqlalchemy import func, select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from database.models.product import Product, Base, Brand, Product_Type

bind_words = [
    'plus',
    'pro',
    'max',
    'ultra',
    'neo',
    'lite',
    'ne'
]

BAD_CHARS_RE = re.compile(r"[^\w\s]+", flags=re.UNICODE)


async def no_digits(text_str: str) -> bool:
    for char in text_str:
        if char.isdigit():
            return False
    return True


async def check_tsv(words: list, tsv: str) -> bool:
    for word in words:
        if word == tsv:
            return True
        if await no_digits(text_str=word):
            if word[:-1] == tsv:
                return True
    return False


async def check_binding_words(search_words: list, tsv_list: list) -> bool:
    for word in search_words:
        if word in bind_words:
            if word in tsv_list:
                return True
            else:
                return False
    return True


def query_string_formating(text_string: str) -> list[str]:
    cleaned = text_string.replace("+", " plus ")
    cleaned = BAD_CHARS_RE.sub(" ", cleaned.lower())
    result: list[str] = list()
    i = 0
    while i < len(cleaned):
        matched = False
        for phrase in bind_words:
            if cleaned.startswith(phrase, i):
                result.append(phrase)
                i += len(phrase)
                matched = True
                break
        if not matched:
            result.append(cleaned[i])
            i += 1
    tokens = [tok for tok in "".join(result).split()]
    return tokens


async def search_devices(session: AsyncSession,
                         query_string: str,
                         conditions: dict[str, Any] = None) -> dict | None:
    query_words = query_string_formating(text_string=query_string)
    tsquery_string = " | ".join(query_words)
    ts_query = func.to_tsquery('simple', tsquery_string)
    query = select(Product,
                   func.ts_rank(Product.title_tsv, ts_query).label('rank'),
                   func.length(Product.title_tsv).label('length')).options(
        joinedload(Product.brand), joinedload(Product.product_type))
    where_conditions = list()
    if conditions:
        for column, value in conditions.items():
            column_attr = getattr(Product, column)
            where_conditions.append(column_attr == value)
    query = query.filter(and_(
        func.length(Product.title_tsv) >= 1),
        Product.title_tsv.op('@@')(ts_query), *where_conditions)
    query = query.order_by(text('rank DESC')).limit(5)
    execute_obj = await session.execute(query)
    for line in execute_obj.all():
        result = line[0]
        device_obj = dict()
        tsv_list = [tsj_obj.split(':')[0].strip("'") for tsj_obj in result.title_tsv.split()]
        fail_tsv_attributes = tsv_list.copy()
        for tsv in tsv_list:
            tsv_value = await check_tsv(words=query_words, tsv=tsv)
            if tsv_value:
                device_obj.setdefault(result.title, []).append(True)
                fail_tsv_attributes.remove(tsv)
            else:
                device_obj.setdefault(result.title, []).append(False)
        tsv_check = await check_binding_words(search_words=query_words, tsv_list=tsv_list)
        if all(device_obj[result.title]) and (not fail_tsv_attributes) and tsv_check:
            return {"title": result.title_line, "brand": result.brand.brand,
                    "product_type": result.product_type.type, "info": result.info,
                    "pros_cons": result.pros_cons, "source": result.source}


def format_tsquery(input_string: str) -> list:
    cleaned = input_string.lower().replace("+", " plus ")
    cleaned = BAD_CHARS_RE.sub(" ", cleaned)
    tokens = [tok for tok in cleaned.split()]
    return tokens


async def search_device_forced(session: AsyncSession, query_string: str):
    ts_query = func.to_tsquery('simple', format_tsquery(query_string))
    query = select(Product,
                   func.ts_rank(Product.title_tsv, ts_query).label('rank'),
                   func.length(Product.title_tsv).label('length')).options(
        joinedload(Product.brand), joinedload(Product.product_type))
    query = query.order_by(text('rank DESC')).limit(10)
    execute_obj = await session.execute(query)
    result = execute_obj.scalars().all()
    return {'result': result}


async def search_product_by_model(session: AsyncSession,
                                  query_string: str,
                                  model: type(Base), tsv_column: InstrumentedAttribute) -> type(Base) | None:
    tsquery_string = " | ".join(format_tsquery(query_string))
    ts_query = func.to_tsquery('simple', tsquery_string)
    query = select(model,
                   func.ts_rank(tsv_column, ts_query).label('rank'),
                   func.length(tsv_column).label('length'))
    query = query.filter(tsv_column.op('@@')(ts_query))
    query = query.order_by(text('rank DESC')).limit(1)
    execute_obj = await session.execute(query)
    for line in execute_obj.all():
        return line[0]


async def fetch_items_from_post(
    session: AsyncSession,
    brand: str | None,
    ptype: str | None
) -> list[dict]:
    stmt = (
        select(
            Product.title_line,
            Brand.brand.label("brand_name"),
            Product_Type.type.label("ptype"),
            Product.info,
            Product.pros_cons,
            Product.source,
        )
        .select_from(Product)
        .join(Brand, Product.brand_id == Brand.id)
        .join(Product_Type, Product.product_type_id == Product_Type.id)
    )

    if brand is not None:
        stmt = stmt.where(Brand.brand == brand)

    if ptype is not None:
        stmt = stmt.where(Product_Type.type == ptype)

    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "title": row.title_line,
            "brand": row.brand_name,
            "product_type": row.ptype,
            "source": row.source,
            "info": row.info,
            "pros_cons": row.pros_cons,
        }
        for row in rows
    ]

