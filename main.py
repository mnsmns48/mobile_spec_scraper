import asyncio
from fastapi import FastAPI

from base import start
from api.views import info_router


async def main():
    await start()


app = FastAPI()
app.include_router(router=info_router, tags=["post_views"])
if __name__ == "__main__":
    asyncio.run(main())
