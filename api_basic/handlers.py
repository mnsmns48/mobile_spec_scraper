from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from api_basic.router_points import templates


async def validation_failed_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "validation_error.html",
        {"request": request, "message": exc.detail}, status_code=exc.status_code)


async def not_found_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "not_found_error.html",
        {"request": request, "message": exc.detail}, status_code=exc.status_code)


async def authorization_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "message": exc.detail}, status_code=exc.status_code)


def register_handlers(app: FastAPI):
    app.exception_handler(422)(validation_failed_exception_handler)
    app.exception_handler(404)(not_found_error_handler)
    app.exception_handler(401)(authorization_handler)
