from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from discord.ext.commands import Cog
from discord.ext.commands.errors import CommandNotFound
from polyleven import levenshtein

from .logic import TypoClient

if TYPE_CHECKING:
    from ..utils.types import AnyBot
    from .cache import CacheABC

__all__ = (
    "similarity_func_factory",
    "TypoSuggest"
)

def similarity_func_factory(max_threshold: int = None) -> Callable[[str, str], int]:
    if max_threshold is None:
        return levenshtein
    else:
        return lambda x, y: levenshtein(x, y, max_threshold)

# TODO:: [Add statistics]

class TypoSuggest(Cog):
    def __init__(self, bot: AnyBot, distance_func: Callable[[str, str], int] = None, cache: CacheABC = None, detect_sub_cmd_typo: bool = False) -> None:
        if distance_func is None:
            distance_func = similarity_func_factory(5)
        self.bot = bot
        self.typo_client = bot.typo_client = TypoClient(bot, distance_func, cache)
        self.sub_cmd_typo = detect_sub_cmd_typo

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # Dont waste time on handled errors
        if hasattr(error, "handled"):
            return

        if isinstance(error, CommandNotFound):
            typo = await self.typo_client.process_typo(ctx)
            if not typo:
                return
            self.bot.dispatch("command_typo", ctx, typo)

    @Cog.listener()
    async def on_command_completion(self, ctx):
        if self.sub_cmd_typo:
            typo = await self.typo_client.process_typo(ctx)
            if not typo:
                return
            self.bot.dispatch("command_typo", ctx, typo)
