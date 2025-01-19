import asyncio

from core.search_device import query_string_formating


async def test_main():
    await query_string_formating(text_string="Смартфон Xiaomi Redmi Note 13 Pro+ 5G 8/256Gb Frost Blue РСТ")


if __name__ == "__main__":
    asyncio.run(test_main())
