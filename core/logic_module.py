from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from config import logger
from config.setup_product_type import detect_device_type
from core.crud import write_data
from core.pw_module import open_link
from core.bs4 import get_bs4_func
from database.models import Devices


async def pars_link(url: str) -> dict:
    func = await get_bs4_func(url=url)
    if func:
        html = await open_link(url=url)
        soup = BeautifulSoup(markup=html, features='lxml')
        result = await func(soup=soup)
        if isinstance(result, dict):
            result.update({'link': url, 'source': func.__name__, 'product_type': await detect_device_type(url)})
            return result


async def add_new_one(session: AsyncSession):
    data = await pars_link(url='https://www.gsmarena.com/xiaomi_redmi_note_12-12063.php')
    if data:
        data.update({'create': datetime.now()})
        await write_data(session=session, table=Devices, data=data)
    else:
        logger.warning('Error. Data for writing into the database has not been created')

