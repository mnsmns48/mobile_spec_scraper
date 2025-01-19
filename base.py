import json

from core import add_new_one
from core.crud import get_data
from database import setup_db
from database.engine import db
from database.models import Devices


async def start():
    await setup_db()
    async with db.scoped_session() as session:
        await add_new_one(session=session)
        # result = await get_data(session=session, table=Specification)
        #
        # for line in result:
        #     for key, value in line.items():
        #         print(key, value)
        #         print('----------------')