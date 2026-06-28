from fastapi import APIRouter, Depends

from api_auth.dependencies.api_connect import verify_service_token
from api_auth.dependencies.fastapi_users_dep import current_super_user
from api_basic.router.api_v1_router import api_v1_router
from api_basic.router.api_v2_router import api_v2_router

from api_basic.router.template_router import template_router

basic_router = APIRouter()

basic_router.include_router(template_router, dependencies=[Depends(current_super_user)])
basic_router.include_router(api_v1_router, dependencies=[Depends(current_super_user)])
basic_router.include_router(api_v2_router, dependencies=[Depends(verify_service_token)])
