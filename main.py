import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api_auth.routers import auth_api_router
from api_basic.routers import basic_router
from api_basic.handlers import register_handlers

from config.settings import app_setup

app = FastAPI(docs_url=app_setup.docs_url)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
app.include_router(router=basic_router)
app.include_router(router=auth_api_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
register_handlers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=app_setup.app_port)
