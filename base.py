from core import add_new_one
from database import setup_db
from database.engine import db


async def start():
    await setup_db()
    async with db.scoped_session() as session:
        await add_new_one(session=session)
