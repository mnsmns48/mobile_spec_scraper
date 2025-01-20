import json
import re
import sys
from typing import Callable
from bs4 import BeautifulSoup
from config import logger
from core.utils import replace_spec_symbols


async def dict_result_prepare(title: str, info: list, pros_cons: list = None) -> dict:
    result = dict()
    replaced_title = await replace_spec_symbols(text=title.lower())
    name_split = replaced_title.split(' ')
    result.update({
        'title': ' '.join(name_split[1:]).strip() if len(name_split) >= 3 else replaced_title,
        'brand': name_split[0],
        'info': json.dumps(info, indent=4)
    })
    return result


async def extract_source_from_url(url: str) -> str | None:
    match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.', url)
    if not match:
        logger.info('URL parsing error')
        return
    else:
        result = match.group(1)
        return result


async def get_bs4_func(url: str) -> Callable | None:
    source = await extract_source_from_url(url=url)
    func = getattr(sys.modules[__name__], source, None)
    if func:
        return func
    else:
        logger.info(f'Link to unknown resource. No function to process "{source}" site-source')


async def gsmarena(soup: BeautifulSoup) -> dict | None:
    result = dict()
    info = list()
    main = soup.find_all(name='th', attrs={'scope': 'row'})
    categories = sorted(main, key=lambda x: int(x['rowspan']))
    for category in categories:
        keys = category.parent.parent.find_all(name='td', attrs={'class': 'ttl'})
        values = category.parent.parent.find_all(name='td', attrs={'class': 'nfo'})
        category_dict = dict()
        current_key = None
        for key, value in zip(keys, values):
            key_text = key.getText()
            value_text = value.getText().strip()
            if key_text == '\xa0':
                if current_key:
                    category_dict[current_key] += ' ' + value_text
                continue
            current_key = key_text
            category_dict[current_key] = value_text
        info.append({category.getText(): category_dict})
    if info:
        title = soup.find(name='h1', attrs={'class': 'specs-phone-name-title'}).getText()
        result = await dict_result_prepare(title=title, info=info)
        return result
    else:
        logger.info('The device information block does not contain INFO-data. Check The link')


async def nanoreview(soup: BeautifulSoup) -> dict | None:
    info = list()
    categories = soup.select('div.card:has(> table.specs-table)')
    for category in categories:
        title_category = category.find('h3', attrs={'class': 'title-h2'})
        keys = category.find_all(name='td', attrs={'class': 'cell-h'})
        values = category.find_all(name='td', attrs={'class': 'cell-s'})
        category_dict = dict()
        for key, value in zip(keys, values):
            category_dict[key.getText().strip()] = value.getText().strip()
        info.append({title_category.getText(): category_dict})
    if info:
        title = soup.find(name='h1', attrs={'class': 'title-h1'}).getText()
        result = await dict_result_prepare(title=title, info=info)
        result.update(
            {
                'advantage': [i.find_previous().getText() for i in soup.find_all(class_='icn-plus-css')],
                'disadvantage': [i.find_previous().getText() for i in soup.find_all(class_='icn-minus-css')],
            }
        )
        return result
    else:
        logger.info('The device information block does not contain INFO-data. Check The link')
