from fastapi import APIRouter

from api.schemas import Info, Link
from core import add_new_one
from core.search_device import search_devices

from database.engine import db

info_router = APIRouter()


@info_router.post("/get_info/")
async def get_info(data: Info):
    conditions = dict()
    for k, v in data.__dict__.items():
        if v != 'string':
            conditions.update({k: v})
    conditions.pop('title')
    async with db.scoped_session() as session:
        result = await search_devices(session=session,
                                      query_string=data.title,
                                      conditions=conditions
                                      )
    return result


@info_router.post("/add_info/")
async def add_info(link: Link):
    conditions = dict()
    for k, v in link.__dict__.items():
        if v != 'string':
            conditions.update({k: v})
    conditions.pop('url')
    async with db.scoped_session() as session:
        result = await add_new_one(session=session, url=link.url, conditions=conditions)
    return result


@info_router.get("/")
async def welcome():
    return 'it works'
