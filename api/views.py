import asyncio

from fastapi import APIRouter, Form, Depends, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from api.schemas import Info, Link, take_form_result
from core import add_new_one
from core.search_device import search_devices
from database.engine import db

info_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@info_router.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@info_router.post("/get_one/")
async def get_one(data: Info):
    conditions = dict()
    for k, v in data.__dict__.items():
        if v != 'string':
            conditions.update({k: v})
    conditions.pop('title')
    print(conditions)
    async with db.scoped_session() as session:
        result = await search_devices(session=session,
                                      query_string=data.title,

                                      conditions=conditions
                                      )
    return result


@info_router.post("/get_many/")
async def get_many(many_items: list[str]):
    result = dict()
    async with db.scoped_session() as session:
        for item in many_items:
            found = await search_devices(session=session, query_string=item)
            if found:
                result.update({item: found})
            await asyncio.sleep(0.1)
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


@info_router.get("/add_url", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse("add_url.html", {"request": request})


@info_router.post("/submit", response_class=HTMLResponse)
async def submit_link(request: Request, form: Link = Depends(take_form_result)):
    if not form.url:
        return templates.TemplateResponse("add_url.html", {"request": request})
    result = await add_info(form)
    if result.get('error'):
        return templates.TemplateResponse("error.html", {"request": request, "result": result['response']})
    return templates.TemplateResponse("fetch_url.html", {"request": request, "result": result})
