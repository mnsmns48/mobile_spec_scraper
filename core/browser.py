import json

from playwright.async_api import Playwright, Browser, Error

from config import pw_conf, logger
from core.utils import get_proxy_file, check_proxy_availability


async def run_browser(playwright: Playwright) -> Browser:
    proxy = dict()
    if pw_conf.enable_proxy:
        proxy_file = await get_proxy_file()
        if proxy_file:
            with open(proxy_file) as proxies:
                proxies_data = json.load(proxies)
            for proxy_elem in proxies_data:
                result = await check_proxy_availability(proxy=proxy_elem)
                if not result:
                    logger.info(f'Non-working proxy {proxy_elem['server']} when selected enable_proxy=True')
                    continue
                else:
                    proxy.update(proxy_elem)
                    break
    if not proxy:
        proxy = None
    browser = await playwright.chromium.launch(headless=pw_conf.headless_mode, proxy=proxy)
    return browser
