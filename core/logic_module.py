from datetime import datetime
from typing import Any, Coroutine, Callable

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from config import logger
from config.setup_product_type import detect_device_type
from core.crud import write_data
from core.pw_module import open_link
from core.bs4 import get_bs4_func
from database.models import DigitalTube


async def pars_link(url: str) -> None | dict:
    func = await get_bs4_func(url=url)
    if isinstance(func, Callable):
        html = await open_link(url=url)
        if isinstance(html, str):
            soup = BeautifulSoup(markup=html, features='lxml')
            parsing_result = await func(soup=soup, url=url)
            if not parsing_result.get('error'):
                parsing_result.update(
                    {'link': url, 'source': func.__name__, 'product_type': await detect_device_type(url)})
                return parsing_result
            return {'error': True, 'response': parsing_result['response']}
        else:
            return {'error': True, 'response': html['response']}
    else:
        return {'error': True, 'response': func['response']}


async def add_new_one(session: AsyncSession,
                      url: str,
                      conditions: dict[str, Any] = None) -> dict:
    parsing_result = await pars_link(url=url)
    if not parsing_result.get('error'):
        if conditions:
            parsing_result.update(conditions)
        parsing_result.update({'create': datetime.now()})
        upload_status = await write_data(session=session, table=DigitalTube, data=parsing_result)
        parsing_result.update({'response': upload_status})
        logger.info(f"{upload_status}: {parsing_result['title']} from {parsing_result['link']}")
        return parsing_result
    else:
        error_msg = parsing_result['response']
        logger.warning(error_msg)
        return {'error': True, 'response': error_msg}


