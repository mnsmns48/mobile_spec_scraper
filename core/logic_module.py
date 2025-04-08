from datetime import datetime
from typing import Any, Callable

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from config import logger
from core.crud import write_data, add_new_brand, get_missing_products
from core.pw_module import open_link
from core.bs4 import get_bs4_func, title_result_prepare
from core.search_device_module import search_product_by_model
from core.utils import url_to_short_string
from database.engine import db
from database.models import Product, Product_Type, Brand


async def pars_link(url: str) -> None | dict:
    func = await get_bs4_func(url=url)
    if isinstance(func, Callable):
        html = await open_link(url=url)
        if isinstance(html, str):
            soup = BeautifulSoup(markup=html, features='lxml')
            parsing_result = await func(soup=soup, url=url)
            async with db.scoped_session() as session:
                parsed_url_string = await url_to_short_string(url=url, resource_name=func.__name__)
                product_type: Product_Type = await search_product_by_model(session=session,
                                                                           query_string=parsed_url_string,
                                                                           model=Product_Type,
                                                                           tsv_column=Product_Type.kind_tsv)
                brand: Brand = await search_product_by_model(session=session,
                                                             query_string=parsed_url_string,
                                                             model=Brand,
                                                             tsv_column=Brand.brand_depends_tsv)
                parsing_result = await title_result_prepare(bs_result=parsing_result)
                if not brand:
                    brand = await add_new_brand(session=session, title=parsing_result['title_line'])
            if not parsing_result.get('error'):
                parsing_result.update(
                    {'link': url,
                     'source': func.__name__,
                     'product_type_id': product_type.id if product_type else 3,
                     'brand_id': brand.id})
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
        upload_status = await write_data(session=session, table=Product, data=parsing_result)
        parsing_result.update({'response': upload_status})
        logger.info(f"{upload_status}: {parsing_result['title']} from {parsing_result['link']}")
        return parsing_result
    else:
        error_msg = parsing_result['response']
        logger.warning(error_msg)
        return {'error': True, 'response': error_msg}


async def get_nanoreview_list_for_parsing(url: str):
    html = await open_link(url=url)
    if isinstance(html, str):
        soup = BeautifulSoup(markup=html, features='lxml')
        links = soup.find_all(name='a', attrs={'style': 'font-weight:500;'})
        products = list()
        for line in links:
            products.append({'a': 'https://nanoreview.net' + line.get('href'), 'title': line.getText()})
        async with db.scoped_session() as session:
            products = await get_missing_products(session=session, products=products)
        return products
    else:
        return {'error': True, 'response': html['response']}
