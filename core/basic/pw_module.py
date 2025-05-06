import logging

from playwright.async_api import async_playwright
from core.basic.browser import run_browser
from playwright_stealth import stealth_async


async def open_link(url: str) -> str | dict:
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        await context.set_extra_http_headers(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/100.0.4896.75 Safari/537.36",
             "Accept-Language": "en-US,en;q=0.9",
             "Referer": "https://google.com"})
        page = await context.new_page()
        await stealth_async(page)
        await page.goto(url=url, wait_until='domcontentloaded')
        html = await page.locator("xpath=//body").inner_html()
        if html:
            return html
        error_msg = f'Error HTML-code in {url}'
        logging.info(error_msg)
        return {'response': error_msg, 'error': 1}
