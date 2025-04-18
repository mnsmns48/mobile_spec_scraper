from fastapi import APIRouter
from starlette.templating import Jinja2Templates

from api.dependencies.backend import authentication_backend
from api.dependencies.fastapi_users import fastapi_users

get_info_router = APIRouter(tags=['Get'])
post_info_router = APIRouter(tags=['Post'])
auth_router = APIRouter(tags=['Auth'])
auth_router.include_router(fastapi_users.get_auth_router(authentication_backend))
templates = Jinja2Templates(directory="templates")
