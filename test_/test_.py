import asyncio
import re

from core.search_device import search_devices
from database.engine import db

smartphone_list = """
S23 S911B 8/128 Black  39000
S23 S911B 8/128 Cream  38500
S23 S911B 8/128 Green  39000
S23 S911B 8/128 Lavender  39000
S23 S911B 8/256 Cream  43000
S23 S911B 8/256 Green  44000
S23 S911B 8/256 Lavender  44200
S23 Ultra S918B 12/256 Black  65200
S24+ S926B 12/256 Cobalt Violet  54200
S24+ S926B 12/256 Marble Gray 🇹🇭 54900
S24+ S926B 12/256 Onyx Black  54200
S24+ S926B 12/512 Onyx Black 🇲🇾 62700
S24 S9210 8/256 Marble Gray  47000
S24 S921B 8/256 Onyx Black  46600
S24 FE S721B 8/256 Blue  38200
S24 FE S721B 8/256 Graphite  38400
S24 FE S721B 8/256 Gray  37800
S24 FE S721B 8/512 Blue 🇲🇾 50200
S24 FE S721B 8/512 Graphite 🇲🇾 50700
S24 FE S721B 8/512 Gray 🇲🇾 50700
S24 Ultra S928B 12/1Tb Titanium Black  95700
S24 Ultra S928B 12/1Tb Titanium Violet  95200
S24 Ultra S928B 12/1Tb Titanium Yellow  95200
S24 Ultra S928B 12/256 Titanium Black  68900
S24 Ultra S928B 12/256 Titanium Gray  68500
S24 Ultra S928B 12/256 Titanium Green  69200
S24 Ultra S928B 12/256 Titanium Violet  69200
S24 Ultra S928B 12/256 Titanium Yellow  68700
S24 Ultra S928B 12/512 Titanium Black  77700
S24 Ultra S928B 12/512 Titanium Gray  77700
S24 Ultra S928B 12/512 Titanium Yellow  76700
S25 S931B 12/256 Icyblue  60700
S25 S931B 12/256 Mint  60700
S25 S931B 12/256 Navy  60700
S25+ S936B 12/256 Icyblue  66000
S25+ S936B 12/256 Silver Shadow  66200
S25+ S936B 12/512 Mint  73400
S25+ S936B 12/512 Navy  73400
S25+ S936B 12/512 Silver Shadow  73200
S25 Ultra S938B 12/1Tb Titanium Gray  108700
S25 Ultra S938B 12/1Tb Titanium Jadegreen  109000
S25 Ultra S938B 12/1Tb Titanium Whitesilver  108700
S25 Ultra S938B 12/256 Titanium Gray  81900
S25 Ultra S938B 12/256 Titanium Silverblue  82000
S25 Ultra S938B 12/256 Titanium Whitesilver  81300
S25 Ultra S938B 12/512 Titanium Black  90500
S25 Ultra S938B 12/512 Titanium Gray  90200
S25 Ultra S938B 12/512 Titanium Silverblue  90200
S25 Ultra S938B 12/512 Titanium Whitesilver  90500
S25 Ultra S938B 12/512 Titanium Whitesilver  90500
S25 Ultra S9380 16/1Tb Titanium Gray  114200
S25 Ultra S9380 16/1Tb Titanium Silverblue  112200
S25 Ultra S9380 16/1Tb Titanium Whitesilver  112200
Смартфон Samsung Galaxy M55S 8Gb/128Gb Зеленый—-21500
Смартфон Samsung Galaxy M55S 8Gb/128Gb Черный—-21500
Смартфон Samsung Galaxy M55S 8Gb/256Gb Зеленый—26800
Смартфон Samsung Galaxy M55S 8Gb/256Gb Черный—26800

"""

def sanitize_tsquery(query):
    return re.sub(r'[^\w\s]', '', query)

async def test_main():
    async with db.scoped_session() as session:
        for smartphone in smartphone_list.split('\n'):
            r = await search_devices(session=session, query_string=sanitize_tsquery(smartphone))
            if not r:
                res = await search_devices(session=session, query_string=sanitize_tsquery('galaxy ' + smartphone))
                if res:
                    print(smartphone, ' : ', res.title, res.title_tsv)
            else:
                print(smartphone, ' : ', r.title, r.title_tsv)


if __name__ == "__main__":
    asyncio.run(test_main())
