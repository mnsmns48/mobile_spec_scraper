import asyncio

from core.basic.search_device_module import query_string_formating, search_devices
from database.engine import db


async def test_main():
    async with db.scoped_session() as session:
        string = await search_devices(session=session, query_string="Смартфон Apple iPhone 16 Pro 128 ГБ черный (black titanium)Nano sim+eSim")
    print(string)

if __name__ == "__main__":
    asyncio.run(test_main())
