from typing import Any

from sqlalchemy import func, select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DeviceDescription
from setup.binding_words import bind_words


async def no_digits(text_str: str) -> bool:
    for char in text_str:
        if char.isdigit():
            return False
    return True


async def check_tsv(words: list, tsv: str) -> bool:
    for word in words:
        if word == tsv:
            return True
        if await no_digits(text_str=word):
            if word[:-1] == tsv:
                return True
    return False


async def check_binding_words(search_words: list, tsv_list: list) -> bool:
    for word in search_words:
        if word in bind_words:
            if word in tsv_list:
                return True
            else:
                return False
    return True


async def query_string_formating(text_string: str) -> list:
    input_string = text_string.replace('+', ' plus')
    working_string = input_string.lower()
    for word in bind_words:
        if word in working_string:
            index = working_string.find(word)
            while index != -1:
                original_word = input_string[index:index + len(word)]
                space_before = index > 0 and input_string[index - 1] != ' '
                space_after = index + len(word) < len(input_string) and input_string[index + len(word)] != ' '
                replacement = f"{' ' if space_before else ''}{original_word}{' ' if space_after else ''}"
                input_string = input_string[:index] + replacement + input_string[index + len(word):]
                working_string = input_string.lower()
                index = working_string.find(word, index + len(replacement))
    return working_string.split()


async def search_devices(session: AsyncSession,
                         query_string: str,
                         conditions: dict[str, Any] = None) -> DeviceDescription | None:
    query_words = await query_string_formating(text_string=query_string)
    tsquery_string = " | ".join(query_words)
    ts_query = func.to_tsquery('english', tsquery_string)
    query = select(DeviceDescription,
                   func.ts_rank(DeviceDescription.title_tsv, ts_query).label('rank'),
                   func.length(DeviceDescription.title_tsv).label('length'))
    where_conditions = list()
    if conditions:
        for column, value in conditions.items():
            column = getattr(DeviceDescription, column)
            where_conditions.append(column == value)
    query = query.filter(and_(
        func.length(DeviceDescription.title_tsv) >= 2),
        DeviceDescription.title_tsv.op('@@')(ts_query), *where_conditions)
    query = query.order_by(text('rank DESC')).limit(5)
    execute_obj = await session.execute(query)
    for line in execute_obj.all():
        result = line[0]
        device_obj = dict()
        tsv_list = [tsj_obj.split(':')[0].strip("'") for tsj_obj in result.title_tsv.split()]
        fail_tsv_attributes = tsv_list.copy()
        for tsv in tsv_list:
            tsv_value = await check_tsv(words=query_words, tsv=tsv)
            if tsv_value:
                device_obj.setdefault(result.title, []).append(True)
                fail_tsv_attributes.remove(tsv)
            else:
                device_obj.setdefault(result.title, []).append(False)
        tsv_check = await check_binding_words(search_words=query_words, tsv_list=tsv_list)
        if all(device_obj[result.title]) and (not fail_tsv_attributes) and tsv_check:
            return result
