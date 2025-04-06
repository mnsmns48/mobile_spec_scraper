from fastapi import FastAPI
from starlette.requests import Request

from api.errors import ValidationFailedException
from api.routers import templates


async def validation_failed_exception_handler(request: Request, exc: ValidationFailedException):
    return templates.TemplateResponse(
        "validation_error.html",
        {"request": request, "message": exc.detail},
        status_code=exc.status_code
    )


def register_handlers(app: FastAPI):
    app.exception_handler(ValidationFailedException)(validation_failed_exception_handler)
