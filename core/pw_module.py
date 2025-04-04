import logging

from playwright.async_api import async_playwright

from core.browser import run_browser


async def open_link(url: str) -> str | dict:
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url=url, wait_until='domcontentloaded')
        html = await page.locator("xpath=//body").inner_html()
        if html:
            return html
        error_msg = f'Error HTML-code in {url}'
        logging.info(error_msg)
        return {'response': error_msg, 'error': 1}