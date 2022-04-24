import os
from asyncio.events import get_running_loop
from asyncio.queues import Queue
from dataclasses import dataclass
from datetime import datetime
from logging import NOTSET, Formatter, Handler
from typing import TYPE_CHECKING, Final, Literal, Optional, Union, final

from aiohttp.client import ClientSession
from discord import (AsyncWebhookAdapter, Colour, Embed,
                     RequestsWebhookAdapter, Webhook)

if TYPE_CHECKING:
    from logging import LogRecord

wh_log = bool(os.getenv("WEBHOOK_LOGS"))

__all__ = (
    "WebHookUrl",
    "WebHookHandler",
    "EmbedFormatter"
)

@final
@dataclass
class WebHookUrl:
    id: int
    token: str

    def __str__(self) -> str:
        return f"https://discord.com/api/webhooks/{self.id}/{self.token}"


class WebHookHandler(Handler):
    session: Final[ClientSession] = ClientSession()

    def __init__(self, url: Union[str, WebHookUrl], level: Union[int, str] = NOTSET) -> None:
        super().__init__(level=level)
        self.webhook = Webhook.from_url(str(url), adapter=AsyncWebhookAdapter(self.session))
        self._sync_adapter = RequestsWebhookAdapter()
        self._sync_adapter._prepare(self.webhook)
        self.buf: Queue[Embed] = Queue()
        self.formatter = EmbedFormatter()

        self._task = get_running_loop().create_task(self.sender())

    def emit(self, record: LogRecord):
        self.buf.put_nowait(self.format(record))

    def flush(self):
        if self.buf.empty():
            return
        adapter = self.webhook._adapter
        self.webhook._adapter = self._sync_adapter

        while not self.buf.empty():
            emb = self.buf.get_nowait()
            self.webhook.send(embed=emb)

        self.webhook._adapter = adapter

    async def sender(self):
        while True:
            emb = await self.buf.get()
            await self.webhook.send(embed=emb)

    def setFormatter(self, fmt: Formatter | None):
        if fmt is not None and not isinstance(fmt, EmbedFormatter):
            raise TypeError(f"Expected EmbedFormmatter instance got {type(fmt)} instance instead")
        self.formatter = fmt

    def filter(self, record: LogRecord) -> bool:
        return super().filter(record) and wh_log

    def close(self):
        super().close()
        self._task.cancel()
        get_running_loop().create_task(self.session.close())


class EmbedFormatter(Formatter):
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: Literal['%', '$', '{'] = '%', validate: bool = True, embed: Embed = None) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        if embed is None:
            embed = Embed()
        self.emb = embed

    colour_map = {
        'DEBUG': Colour.blue(),       # Blue
        'INFO': Colour.green(),       # Green
        'WARNING': Colour(0xfde64b),  # Yellow
        'ERROR': Colour.orange(),     # Orange
        'CRITICAL': Colour.red(),     # Red
        'UNSET': Colour.blue()        # Blue
    }

    def format(self, record: LogRecord) -> Embed:
        self.emb.timestamp = datetime.fromtimestamp(record.created)
        self.emb.colour = self.colour_map.get(record.levelname, Embed.Empty)
        desc = super().format(record)
        if len(desc) > 2048:
            desc = '```\n' + desc[:2038] + "...```"
        elif len(desc) < 2042:
            desc = "```\n" + desc + "```"
        else:
            desc = "```\n" + desc[:len(desc) - 10] + "...```"
        self.emb.description = desc
        self.emb.title = "%(name)s | %(levelname)s" % record.__dict__
        return Embed
