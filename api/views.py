import asyncio
import re

from fastapi import Depends, Request
from starlette.responses import HTMLResponse

from api.routers import templates, info_router
from api.schemas import Info, Link, take_form_result, ItemList
from core import add_new_one
from api.errors import ValidationFailedException
from core.logic_module import get_url_list_for_parsing
from core.search_device_module import search_devices
from database.engine import db


############################################################### GET #################################################


@info_router.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@info_router.get("/add_url", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse("add_url.html", {"request": request})


@info_router.get("/engineering-menu/")
async def get_engineering_menu(request: Request):
    return templates.TemplateResponse("engineering_menu.html", {"request": request})


############################################################# POST ###############################################


@info_router.post("/get_one/")
async def get_one(data: Info):
    conditions = dict()
    for k, v in data.__dict__.items():
        if v != 'string':
            conditions.update({k: v})
    conditions.pop('title')
    async with db.scoped_session() as session:
        result = await search_devices(session=session, query_string=data.title, conditions=conditions)
    return result


@info_router.post("/get_many/")
async def get_many_items(items: ItemList):
    result = dict()
    async with db.scoped_session() as session:
        for item in items.items:
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


@info_router.post("/submit_one_url", response_class=HTMLResponse)
async def submit_link(request: Request, form: Link = Depends(take_form_result)):
    if not form.url:
        return templates.TemplateResponse("add_url.html", {"request": request})
    result = await add_info(form)
    if result.get('error'):
        return templates.TemplateResponse("error.html", {"request": request, "result": result['response']})
    return templates.TemplateResponse("fetch_url.html", {"request": request, "result": result})


@info_router.post("/submit_pars_all", response_class=HTMLResponse)
async def submit_pars_all(request: Request):
    form_data = await request.form()
    url_for_pars = form_data.get("url")
    pattern = r'^https://nanoreview\.net/(ru|en)/.+/all-.+$'
    if bool(re.match(pattern, url_for_pars)):
        url_list = await get_url_list_for_parsing(url=url_for_pars)
        return templates.TemplateResponse("link_for_pars.html", {"request": request, "url_for_pars": url_list})
    else:
        raise ValidationFailedException(message="URL does not match the expected format")