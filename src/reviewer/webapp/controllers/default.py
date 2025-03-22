"""
Frontend controllers used to deliver HTML/VUE files and static assets.
"""
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .. import app
from ..views import get_components


app.mount("/assets", StaticFiles(directory="./views/assets"), name="static files")


@app.get("/", response_class=HTMLResponse, tags=["frontend"])
def index():
    """
    Returns index html file
    """
    with open("./views/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/components.js", response_class=HTMLResponse, tags=["frontend"])
def vue_components():
    """
    Assembles and returns all the available vue.js components (see webapp/views/assets/js/components).
    """
    components = "\n".join(list(get_components().values()))

    headers = {}
    headers["Content-Type"]  = "application/javascript"
    headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    headers["Pragma"]        = "no-cache"
    headers["Expires"]       = "0"

    return Response(content    = components, 
                    headers    = headers,
                    media_type = "application/javascript")
