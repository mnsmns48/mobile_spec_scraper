import re

from fastapi import APIRouter, Form
from starlette.requests import Request
from starlette.responses import HTMLResponse

from api_basic.errors import ValidationFailedException
from api_basic.router.api_v1_router import add_info
from core.basic.logic_module import get_nanoreview_list_for_parsing
from templates import templates

welcome_router = APIRouter(tags=['Welcome'])
template_router = APIRouter(tags=['Template Router'])


@welcome_router.get("/welcome")
async def welcome():
    return {"status": "ok"}


@welcome_router.get("/")
async def render_start_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@template_router.get("/add_url", response_class=HTMLResponse)
async def add_url(request: Request):
    return templates.TemplateResponse("add_url.html", {"request": request})


@template_router.get("/engineering-menu/")
async def get_engineering_menu(request: Request):
    return templates.TemplateResponse("engineering_menu.html", {"request": request})


@template_router.post("/submit_one_url", response_class=HTMLResponse)
async def submit_link(request: Request, url: str = Form(...)):
    if not url:
        return templates.TemplateResponse("add_url.html", {"request": request})
    result = await add_info(url)
    if result.get('error'):
        return templates.TemplateResponse("error.html", {"request": request, "result": result['response']})
    return templates.TemplateResponse("fetch_url.html", {"request": request, "result": result})


@template_router.post("/submit_pars_all", response_class=HTMLResponse)
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
