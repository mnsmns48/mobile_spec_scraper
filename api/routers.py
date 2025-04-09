from fastapi import APIRouter
from starlette.templating import Jinja2Templates

get_info_router = APIRouter(tags=['Get'])
post_info_router = APIRouter(tags=['Post'])
templates = Jinja2Templates(directory="templates")
