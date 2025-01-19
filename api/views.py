from fastapi import APIRouter

from api.schemas import Info
from core.search_device import search_devices

from database.engine import db
from database.models import Devices

info_router = APIRouter()


# @info_router.post("/check_device/")
# async def check_device(data: Info):
#     async with db.scoped_session() as session:
#         result = await get_data(session=session, table=Devices, conditions={'source': 'gsmarena'})
#     return result


@info_router.post("/check_device/")
async def check_device(data: Info):
    async with db.scoped_session() as session:
        result = await search_devices(session=session, query_string=data.title)
    return result
