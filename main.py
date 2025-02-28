from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from api.views import info_router
from config.settings import app_setup
from database import setup_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_db()
    yield

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(router=info_router, tags=["post_views"])


if __name__ == "__main__":
    uvicorn.run("main:app", port=app_setup.app_port)