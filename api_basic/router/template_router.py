from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from templates import templates

template_router = APIRouter(tags=['Template Router'])


@template_router.get("/welcome")
async def welcome():
    return {"status": "ok"}


@template_router.get("/")
async def render_start_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@template_router.get("/add_url", response_class=HTMLResponse)
async def add_url(request: Request):
    return templates.TemplateResponse("add_url.html", {"request": request})


@template_router.get("/engineering-menu/")
async def get_engineering_menu(request: Request):
    return templates.TemplateResponse("engineering_menu.html", {"request": request})
