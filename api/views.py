from fastapi import APIRouter, Form
from starlette.responses import HTMLResponse
from api.schemas import Info, Link
from core import add_new_one
from core.search_device import search_devices
from database.engine import db

info_router = APIRouter()


@info_router.post("/get_info/")
async def get_info(data: Info):
    conditions = dict()
    for k, v in data.__dict__.items():
        if v != 'string':
            conditions.update({k: v})
    conditions.pop('title')
    async with db.scoped_session() as session:
        result = await search_devices(session=session,
                                      query_string=data.title,
                                      conditions=conditions
                                      )
    return result


@info_router.post("/add_info/")
async def add_info(link: Link):
    conditions = dict()
    for k, v in link.__dict__.items():
        if v != 'string':
            conditions.update({k: v})
    conditions.pop('url')
    async with db.scoped_session() as session:
        result = await add_new_one(session=session, url=link.url, conditions=conditions)
    return result


@info_router.get("/")
async def welcome():
    return 'it works'


@info_router.get("/add", response_class=HTMLResponse)
async def add_link():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Add Link</title>
    </head>
    <body>
        <h1>Add a Link</h1>
        <form action="/submit_link" method="post">
            <label for="link">Link:</label>
            <input type="text" id="link" name="link"><br>
            <label for="title">Title:</label>
            <input type="text" id="title" name="title"><br>
            <label for="brand">Brand:</label>
            <input type="text" id="brand" name="brand"><br>
            <label for="product_type">Product Type:</label>
            <input type="text" id="product_type" name="product_type"><br>
            <label for="source">Source:</label>
            <input type="text" id="source" name="source"><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@info_router.post("/submit_link", response_class=HTMLResponse)
async def submit_link(link: str = Form(...), title: str = Form('string'), brand: str = Form('string'),
                      product_type: str = Form('string'), source: str = Form('string')):
    url = Link(url=link, title=title, brand=brand, product_type=product_type, source=source)
    print(url.title)
    result = await add_info(link=url)
    return HTMLResponse(content=f"""
    <h1>Result:</h1>
    """)
    # <p>Link: {link}</p>
    # <p>Title: {title}</p>
    # <p>Brand: {brand}</p>
    # <p>Product Type: {product_type}</p>
    # <p>Source: {source}</p>
    # <p>Result: {result}</p>
    # <a href="/add">Add</a>