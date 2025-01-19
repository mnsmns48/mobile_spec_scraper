from sqlalchemy import func, select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Devices
from setup.binding_words import bind_words


async def no_digits(text_str: str) -> bool:
    for char in text_str:
        if char.isdigit():
            return False
    return True


# async def tsv_process(words: list, tsv: str) -> bool:
#     if await no_digits(text_str=tsv) and len(tsv) >= 3:
#         tsv_ = tsv[:-1]
#     else:
#         tsv_ = tsv
#     print(f"{tsv_}: {words}")
#     for word in words:
#         if tsv_ in word:
#             return True
#     return False

async def tsv_process(words: list, tsv: str) -> bool:
    for word in words:
        if word == tsv or word[:-1] == tsv:
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
                space_after = (index + len(word) < len(input_string) and
                               input_string[index + len(word)] != ' ')
                replacement = f"{' ' if space_before else ''}{original_word}{' ' if space_after else ''}"
                input_string = input_string[:index] + replacement + input_string[index + len(word):]
                working_string = input_string.lower()
                index = working_string.find(word, index + len(replacement))
    return working_string.split()


async def search_devices(session: AsyncSession, query_string: str):  # -> list[Devices] | None
    words = await query_string_formating(text_string=query_string)
    tsquery_string = " | ".join(words)
    ts_query = func.to_tsquery('english', tsquery_string)
    query = (select(Devices,
                    func.ts_rank(Devices.title_tsv, ts_query).label('rank'),
                    func.length(Devices.title_tsv).label('length'))
             .filter(and_(func.length(Devices.title_tsv) >= 2),
                     Devices.title_tsv.op('@@')(ts_query)).order_by(text('rank DESC')).limit(5))
    execute_obj = await session.execute(query)
    result_scalars = execute_obj.all()
    result = list()
    for line in result_scalars:
        item_dict = dict()
        tsv_list = [part.split(':')[0].strip("'") for part in line[0].title_tsv.split()]
        tsv_list_true = tsv_list.copy()
        for key in tsv_list:
            tsv_process_obj = await tsv_process(words=words, tsv=key)
            if tsv_process_obj:
                item_dict.setdefault(line[0].title, []).append(True)
                tsv_list_true.remove(key)
            else:
                item_dict.setdefault(line[0].title, []).append(False)
        tsv_check = await check_binding_words(search_words=words, tsv_list=tsv_list)
        if all(item_dict[line[0].title]) and (not tsv_list_true) and tsv_check:
            result.append(line[0])
            break
    if result:
        r = list()
        for line in result:
            r.append(line.title)
        print(' '.join(r))
        return ' '.join(r)
    return None
