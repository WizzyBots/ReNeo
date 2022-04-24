from os import getenv
from sys import argv
from pathlib import Path

from aiohttp import web
from aiohttp_jinja2 import render_template_async

try:
    dev = (("-d" in argv) or ("--dev" in argv)) or not getenv("STATIC")
except:
    dev = False

STATIC_ROUTE_NAME = "/static"

routes = web.RouteTableDef()

@routes.view('/') # needs opts
class Index(web.View):
    async def get(self):
        return await render_template_async("index.html.jinja", self.request, {})

if dev:
    routes.static(STATIC_ROUTE_NAME, Path(__file__).parent / "resources" / "static",  append_version=True)
