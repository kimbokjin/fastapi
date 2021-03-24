from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount("/static", StaticFiles(directory="C:\\Users\\Admin\\Desktop\\fastapi\\static"), name="static")


templates = Jinja2Templates(
    directory="C:\\Users\\Admin\\Desktop\\fastapi\\static\\templates")


@app.get("/", response_class=HTMLResponse)
async def read_item():
    return """
        <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>

    """


@app.get("/items/", response_class=HTMLResponse)
async def read_items():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look MEEEEEEEEEEEE! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/hi/", response_class=HTMLResponse)
async def hi_page(request: Request):
    return templates.TemplateResponse("item.html", {"request": request})
