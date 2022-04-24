import logging
from typing import Awaitable, Callable
from discord.ext.commands.context import Context

from discord.utils import escape_markdown
from neobot.core.utils.context import NeoEmbed
from discord.errors import HTTPException

from discord.ext.commands import command, Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import bot_has_permissions, cooldown
from discord.ext.commands.errors import BotMissingPermissions, CheckFailure, CommandInvokeError, CommandOnCooldown, MissingRequiredArgument

from .converters import BinaryStrConv, HexStrConv, DecStrConv, text_conv_factory, InvalidInput
from neobot.core.utils import get_emoji

logger = logging.getLogger(__name__)

class Text(Cog):
    # cooldown config #
    uses = 2
    period = 5.0

    def __init__(self) -> None:
        self.check: Callable[[Context], Awaitable[bool]] = bot_has_permissions(send_messages=True, embed_links=True).predicate

    @staticmethod
    async def send_processed(ctx: NeoEmbed, content: str, _mode: str) -> None:
        async with ctx.std_embed() as em:
            em.title = get_emoji("YES") + f" | {_mode} Content"
            if _mode == "Encoded":
                em.description = '```\n' + content + '\n```'
            else:
                em.description = escape_markdown(content)

    @cooldown(uses, period, BucketType.member)
    @command(name="tobinary", aliases=["tobin"])
    async def _tobin(self, ctx: NeoEmbed, *, content: text_conv_factory("tobinary", "0>8b")) -> None: # type: ignore
        await self.send_processed(ctx, content, "Encoded")

    @cooldown(uses, period, BucketType.member)
    @command(name="tohex", aliases=["tohexadecimal"])
    async def _tohex(self, ctx: NeoEmbed, *, content: text_conv_factory("tohex", "X")) -> None: # type: ignore
        await self.send_processed(ctx, content, "Encoded")

    @cooldown(uses, period, BucketType.member)
    @command(name="todec", aliases=["todecimal"])
    async def _todec(self, ctx: NeoEmbed, *, content: text_conv_factory("todec", "d")) -> None: # type: ignore
        await self.send_processed(ctx, content, "Encoded")

    @cooldown(uses, period, BucketType.member)
    @command(name="frombin", aliases=["fbin", "fbinary", "frombinary"])
    async def _fbin(self, ctx: NeoEmbed, *, content: BinaryStrConv) -> None:
        await self.send_processed(ctx, content, "Decoded")

    @cooldown(uses, period, BucketType.member)
    @command(name="fromdec", aliases=["fdec", "fdecimal", "fromdecimal"])
    async def _fdec(self, ctx: NeoEmbed, *, content: DecStrConv) -> None:
        await self.send_processed(ctx, content, "Decoded")

    @cooldown(uses, period, BucketType.member)
    @command(name="fromhex", aliases=["fhex", "fhexadecimal", "fromhexadecimal"])
    async def _fhex(self, ctx: NeoEmbed, *, content: HexStrConv) -> None:
        await self.send_processed(ctx, content, "Decoded")

    async def cog_check(self, ctx) -> bool:
        return await self.check(ctx)

    async def cog_command_error(self, ctx: NeoEmbed, error) -> None:
        # Let these errors be handled by the bot
        if isinstance(error, BotMissingPermissions):
            return

        if isinstance(error, InvalidInput):
            async with ctx.std_embed() as em:
                em.title = get_emoji("NO", 1) + " | Invalid Input"
                _bt = "\`"
                em.description = f"Invalid parameter `{error.argument.replace('`', _bt)}` for command `{ctx.command}`"
            error.handled = True
            return

        if isinstance(error, MissingRequiredArgument):
            async with ctx.std_embed() as em:
                em.title = get_emoji("NO", 1) + " | Missing Required Parameter"
                _bt = "\`"
                em.description = f"No content found to {('en', 'de')['from' in (cmd := str(ctx.command))]}code for command `{cmd}`"
            error.handled = True
            return

        if isinstance(error, CommandOnCooldown):
            async with ctx.std_embed() as em:
                em.title = get_emoji("STOP") + " | Cooldown"
                em.description = f"You are going to fast " + get_emoji("FAST") + \
                    f"\nTry again in {error.retry_after:.2f} seconds"
                em.set_footer(text=f"The {ctx.command} command can be used {error.cooldown.rate} times in {error.cooldown.per} seconds")
            error.handled = True
            return

        if isinstance(error, CommandInvokeError):
            if isinstance(error.__cause__, HTTPException):
                em = ctx.std_embed()
                em.title = get_emoji("SAD", 2) + " | Error while sending result"
                em.description = "An error occurred while sending the result" \
                    f"\nFailed with error code `{error.__cause__.code}` and status code `{error.__cause__.status}`" + \
                    "\n\nThe error desciption from discord was:\n" + \
                    '`' + error.__cause__.text + '`'
                await em.send(ctx.author)
                try:
                    await em.send(ctx)
                except:
                    pass
                error.handled = True
                return

        async with ctx.std_embed() as em:
            em.title = get_emoji("SAD", 2) + " | Unexpected Error"
            em.description = f"An unexpected error occurred in the `{ctx.command}` command, I have informed my developer(s)" \
                " of the error."
        logger.error(error, exc_info=True)
        error.handled = True
