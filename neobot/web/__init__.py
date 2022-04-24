try:
    import aiohttp_jinja2
    import jinja2
except (ImportError, ModuleNotFoundError):
    raise

import asyncio
from logging import getLogger
from os import getenv
import threading
from typing import Optional
from aiohttp import web
from pathlib import Path
from discord import Client

from .routes import STATIC_ROUTE_NAME, routes

def setup_app(app: web.Application, client: Client, title: Optional[str] = None) -> None:
    app["neobot.web.client"] = client
    app["neobot.web.title"] = title or client.__class__.__name__
    aiohttp_jinja2.setup(app,
        enable_async = True,
        loader=jinja2.FileSystemLoader(str(Path(__file__).parent / "resources"))) \
        .globals["len"] = len
    app.add_routes(routes)
    app["static_root_url"] = getenv("STATIC") or STATIC_ROUTE_NAME

def run_threaded(client: Client, title: Optional[str] = None):
    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = web.Application()
        setup_app(app, client, title)
        _logger = getLogger("neobot.web")
        getLogger("aiohttp.access").setLevel("WARNING")
        _logger.info("Starting server.")
        web.run_app(app, print=lambda x: _logger.info(x.replace("\n", " | ")))
        if not loop.is_closed():
            loop.close()
        _logger.info("======= Server closed. =======")

    thr = threading.Thread(target=runner, name="aiohttp-server", daemon=True)
    thr.start()

def main(client: Client):
    run_threaded(client, "NeoBot")
