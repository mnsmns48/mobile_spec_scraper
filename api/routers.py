from fastapi import APIRouter
from starlette.templating import Jinja2Templates

info_router = APIRouter()
templates = Jinja2Templates(directory="templates")