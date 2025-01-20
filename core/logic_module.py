from datetime import datetime
from typing import Any

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


async def add_new_one(session: AsyncSession, url: str,
                      conditions: dict[str, Any] = None) -> str:
    data = await pars_link(url=url)
    if data:
        if conditions:
            data.update(conditions)
        data.update({'create': datetime.now()})
        await write_data(session=session, table=Devices, data=data)
        result = f'{data['brand']} {data['title']} added'
        logger.info(result)
        return result
    else:
        result = 'Error. Data for writing into the database has not been created'
        logger.warning(result)
        return result
