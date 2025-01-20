from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.views import info_router
from database import setup_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router=info_router, tags=["post_views"])
