from fastapi import APIRouter

from api_basic.views import (post_info as post_info_router,
                             get_info as get_info_router)

basic_router = APIRouter()
basic_router.include_router(get_info_router)
basic_router.include_router(post_info_router)
