from fastapi import APIRouter

from api_auth.dependencies.backend import authentication_backend
from api_auth.dependencies.fastapi_users import fastapi_users
from api_auth.schemas.user import UserRead, UserCreate

auth_router = APIRouter(tags=['Auth'])
auth_router.include_router(fastapi_users.get_auth_router(authentication_backend))
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))