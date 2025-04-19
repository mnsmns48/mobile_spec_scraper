import asyncio
import re
from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from api_basic.schemas import ItemList

from api_basic.errors import ValidationFailedException
from core.basic.logic_module import add_new_one, get_nanoreview_list_for_parsing
from core.basic.search_device_module import search_devices

from database.engine import db
from templates import templates

############################################################### GET #################################################

get_info = APIRouter(tags=['Get'])


@get_info.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@get_info.get("/add_url", response_class=HTMLResponse)
async def add_url(request: Request):
    return templates.TemplateResponse("add_url.html", {"request": request})


@get_info.get("/engineering-menu/")
async def get_engineering_menu(request: Request):
    return templates.TemplateResponse("engineering_menu.html", {"request": request})


############################################################# POST ###############################################


post_info = APIRouter(tags=['Post'])


@post_info.post("/get_one/")
async def get_one_item(data: str):
    async with db.scoped_session() as session:
        result = await search_devices(session=session, query_string=data)
    return result


@post_info.post("/get_many/")
async def get_many_items(items: ItemList):
    result = dict()
    async with db.scoped_session() as session:
        for item in items.items:
            found = await search_devices(session=session, query_string=item)
            if found:
                result.update({item: found})
            await asyncio.sleep(0.1)
    return result


@post_info.post("/add_info/")
async def add_info(url: str = Form(...)):
    async with db.scoped_session() as session:
        result = await add_new_one(session=session, url=url)
    return result


@post_info.post("/submit_one_url", response_class=HTMLResponse)
async def submit_link(request: Request, url: str = Form(...)):
    if not url:
        return templates.TemplateResponse("add_url.html", {"request": request})
    result = await add_info(url)
    if result.get('error'):
        return templates.TemplateResponse("error.html", {"request": request, "result": result['response']})
    return templates.TemplateResponse("fetch_url.html", {"request": request, "result": result})


@post_info.post("/submit_pars_all", response_class=HTMLResponse)
async def submit_pars_all(request: Request):
    form_data = await request.form()
    url_for_pars = form_data.get("url")
    pattern = r'^https://nanoreview\.net/(ru|en)/.+/all-.+$'
    if bool(re.match(pattern, url_for_pars)):
        url_list = await get_nanoreview_list_for_parsing(url=url_for_pars)
        if url_list:
            return templates.TemplateResponse("link_for_pars.html", {"request": request, "url_for_pars": url_list})
        else:
            return templates.TemplateResponse("no_items.html", {"request": request})
    else:
        raise ValidationFailedException(message="URL does not match the expected format")
