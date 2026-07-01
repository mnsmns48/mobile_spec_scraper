import asyncio

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from api_basic.schemas import ItemList
from core.basic.logic_module import add_new_one
from core.basic.search_device_module import search_product_by_model, search_devices, search_device_forced
from database.engine import db
from database.models import Brand

api_v1_router = APIRouter(tags=['Api V1 UI USER'])


@api_v1_router.post("/get_many/")
async def get_many_items(items: ItemList):
    result = dict()
    async with db.scoped_session() as session:
        for item in items.items:
            found = await search_devices(session=session, query_string=item)
            if found:
                result.update({item: found})
            await asyncio.sleep(0.1)
    return result


@api_v1_router.post("/get_itemlist/")
async def get_many_items(item: str, session: AsyncSession = Depends(db.session_getter)):
    result = await search_device_forced(session=session, query_string=item)
    return result


@api_v1_router.post("/get_brand/")
async def get_brand_by_searchline(item: str, session: AsyncSession = Depends(db.session_getter)):
    result = await search_product_by_model(session=session,
                                           query_string=item, model=Brand, tsv_column=Brand.brand_depends_tsv)
    return result


@api_v1_router.post("/add_info/")
async def add_info(url: str = Form(...)):
    async with db.scoped_session() as session:
        result = await add_new_one(session=session, url=url)
    return result
