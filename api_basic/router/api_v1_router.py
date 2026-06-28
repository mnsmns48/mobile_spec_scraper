import asyncio
import re

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import HTMLResponse

from api_basic.errors import ValidationFailedException
from api_basic.schemas import ItemList
from core.basic.logic_module import add_new_one, get_nanoreview_list_for_parsing
from core.basic.search_device_module import search_product_by_model, search_devices, search_device_forced
from database.engine import db
from database.models import Brand, Product_Type
from templates import templates

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


@api_v1_router.post("/submit_one_url", response_class=HTMLResponse)
async def submit_link(request: Request, url: str = Form(...)):
    if not url:
        return templates.TemplateResponse("add_url.html", {"request": request})
    result = await add_info(url)
    if result.get('error'):
        return templates.TemplateResponse("error.html", {"request": request, "result": result['response']})
    return templates.TemplateResponse("fetch_url.html", {"request": request, "result": result})


@api_v1_router.post("/submit_pars_all", response_class=HTMLResponse)
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
