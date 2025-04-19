from fastapi import APIRouter, Depends

from api_auth.dependencies.fastapi_users_dep import current_super_user
from api_basic.views import (post_info as post_info_router,
                             get_info as get_info_router,
                             start_rt as start_router)
from core.auth.transport import check_authentication

basic_router = APIRouter()

basic_router.include_router(start_router)
basic_router.include_router(get_info_router, dependencies=[Depends(current_super_user)])
basic_router.include_router(post_info_router, dependencies=[Depends(current_super_user)])
