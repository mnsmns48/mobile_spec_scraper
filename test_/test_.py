import asyncio

from core.search_device import query_string_formating

smartphones = [
    "Смартфон Samsung Galaxy A05 4/64 серебрист",
    "Смартфон Samsung Galaxy A05 4/64 салатовый",
    "Смартфон Samsung Galaxy S21 FE 5G 8/128 бе",
    "Смартфон Samsung Galaxy A16 4G 4/128 тёмно",
    "Смартфон Samsung Galaxy A16 4G 4/128 светл",
    "Смартфон Realme Note 50 3/64 Чёрный",
    "Смартфон Realme C61 6/128 зелёный",
    "Смартфон Realme C61 6/128 золотой",
    "Смартфон Realme Note 60x 3/64 зелёный",
    "Смартфон Xiaomi Poco X5 8/256 чёрный",
    "Смартфон Xiaomi Poco X6 Pro 8/256 Чёрный",
    "Смартфон Xiaomi 12 Lite 8/128 розовый",
    "Смартфон Xiaomi Redmi 12 4/128 голубой",
    "Смартфон Xiaomi Redmi A3x 3/64 чёрный",
    "Смартфон Xiaomi Redmi A3x 3/64 белый",
    "Смартфон Xiaomi Redmi 14C 8/256 синий",
    "Смартфон Tecno Pova 6 Neo 8/128 зелёный",
    "Смартфон Tecno Camon 30S 6/128 Чёрный",
    "Смартфон Tecno Camon 30S 6/128 Фиолетовый",
    "Смартфон Infinix Hot 50 4G 6/256 темно-сер",
    "Смартфон Tecno Spark 30 8/256 чёрный",
    "Смартфон Tecno Spark 30 Pro 8/128 чёрный",
    "Смартфон Tecno Spark 30 8/256 белый",
    "Смартфон Tecno Spark 30 Pro 8/256 белый",
    "Смартфон Infinix Hot 50 4G 6/256 чёрный",
    "Смартфон Tecno Spark 30 Pro 8/128 белый",
    "Смартфон Tecno Spark 30 5G 6/128 Чёрный"
]



async def test_main():
    for s in smartphones:
        r = await query_string_formating(text_string=s)
        print(r)

if __name__ == "__main__":
    asyncio.run(test_main())
