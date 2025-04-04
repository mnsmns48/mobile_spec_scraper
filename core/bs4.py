import inspect
import json
import re
import sys
from typing import Callable
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession


async def title_result_prepare(bs_result: dict) -> dict:
    sanitized_title = bs_result['title'].lower().replace('+', ' Plus')
    name_split = sanitized_title.split(' ')
    bs_result.update(
        {'title_line': bs_result['title'],
         'title': ' '.join(name_split[1:]).strip() if len(name_split) >= 3 else sanitized_title}
    )
    return bs_result


async def extract_source_from_url(url: str) -> dict:
    match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.', url)
    if not match:
        error_msg = 'URL parsing error'
        return {'response': error_msg, 'error': True}
    else:
        result = match.group(1)
        return {'url': result}


async def get_bs4_func(url: str) -> dict | Callable:
    source = await extract_source_from_url(url=url)
    if not source.get('error'):
        func = getattr(sys.modules[__name__], source['url'], None)
        if func:
            return func
        else:
            error_msg = f'Link to unknown resource. No function to process <<{source["url"]}>> site-source'
            return {'response': error_msg, 'error': True}
    return {'error': True, 'response': source.get('response')}


def generate_bs4_info_parsing(url: str) -> dict:
    return {
        'response': (
            f'The device information block does not contain INFO-data. '
            f'Error parsing {inspect.currentframe().f_code.co_name.upper()}-function '
            f'or check this URL: {url}'
        ),
        'error': True
    }


async def gsmarena(soup: BeautifulSoup, url: str) -> dict:
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
        return {'title': title, 'info': json.dumps(info, indent=4)}
    else:
        return generate_bs4_info_parsing(url=url)


async def nanoreview(soup: BeautifulSoup, url: str) -> dict:
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
        result = {'title': title, 'info': json.dumps(info, indent=4)}
        advantage = [i.find_previous().getText() for i in soup.find_all(class_='icn-plus-css')]
        disadvantage = [i.find_previous().getText() for i in soup.find_all(class_='icn-minus-css')]
        if advantage or disadvantage:
            result.update({'pros_cons': {'advantage': advantage, 'disadvantage': disadvantage}})
        return result
    else:
        return generate_bs4_info_parsing(url=url)
