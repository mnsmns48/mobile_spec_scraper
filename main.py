from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api.handlers import register_handlers
from api.views import info_router
from config.settings import app_setup
from database import setup_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_db()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"],
                   allow_credentials=True, )
app.include_router(router=info_router, tags=["post_views"])
app.mount("/static", StaticFiles(directory="static"), name="static")
register_handlers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=app_setup.app_port)
