import asyncio
import pathlib, aiohttp
import re

from aiohttp import ClientOSError, ClientHttpProxyError

from config import logger, pw_conf


async def get_proxy_file() -> str | None:
    current_dir = pathlib.Path.cwd()
    parent_dir = current_dir.parent
    files = list(parent_dir.rglob('prox*.json'))
    if files:
        for file in files:
            return file
    logger.info(f"Proxy mode is activated, but proxy file is not found")
    return


async def check_proxy_availability(proxy: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            async with asyncio.timeout(delay=pw_conf.proxy_timeout or 5):
                async with session.get("https://ya.ru",
                                       proxy=f"https://{proxy['server']}:{proxy['port']}") as response:
                    if response.status == 200:
                        return True
        except (ClientOSError, UnboundLocalError, TimeoutError, ClientHttpProxyError):
            return False


async def replace_spec_symbols(text: str) -> str:
    text = text.replace('+', ' Plus')
    return text

