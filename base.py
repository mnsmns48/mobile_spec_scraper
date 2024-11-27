from database import setup_db


async def start():
    await setup_db()
