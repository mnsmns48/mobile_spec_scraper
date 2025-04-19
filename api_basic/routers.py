from fastapi import APIRouter

from api_basic.views import post_info, get_info

basic_router = APIRouter()
basic_router.include_router(get_info)
basic_router.include_router(post_info)
