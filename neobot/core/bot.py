from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Callable, ClassVar, List, Union

from discord.errors import HTTPException
from discord.ext.commands import Bot
from discord.ext.commands import DefaultHelpCommand as _Dh
from discord.ext.commands.errors import (BotMissingPermissions, CheckFailure,
                                         CommandError, CommandInvokeError,
                                         CommandNotFound, DisabledCommand,
                                         MissingPermissions, NoPrivateMessage,
                                         NotOwner, NSFWChannelRequired)

from neobot.core.leven.cog import TypoSuggest, similarity_func_factory
from neobot.core.leven import LRUCache
from neobot.core.utils import EmbedContext, PrefixManager, get_emoji

if TYPE_CHECKING:
    from neobot.core.leven.logic import TypoSuggestion
    from neobot.core.utils.credits import Credits
    from neobot.core.utils.db_abc import DbClientABC

logger = logging.getLogger(__name__)

class NeoBase(Bot):
    def __init__(self, command_prefix: Union[List[str], str], help_command = _Dh(), description = None, *, db_client: DbClientABC = None, **options) -> None:
        self._credits: Credits = [
            {
                "Entity": "[WizzyGeek](https://github.com/WizzyGeek)", # 😎 Yes.
                "Reason": "for Authoring the project"
            },
            {
                "Entity": "[discord.py](https://github.com/Rapptz/discord.py)",
                "Reason": "An API wrapper around the discord API"
            }
        ]

        options.setdefault("strip_after_prefix", True)
        options.setdefault("case_insensitive", True)

        if db_client:
            async def postponed(*args, **kwargs):
                self.command_prefix = await PrefixManager(command_prefix, self, db_client) # postponed eval
                self.remove_listener(postponed, "on_ready")

        super().__init__(command_prefix, help_command, description, **options)
        if db_client:
            self.add_listener(postponed, "on_ready") # type: ignore[pyright]
        if hasattr(self, "setup"):
            self.setup()

    def add_credit(self, *, entity: str, reason: str = None):
        if not reason:
            self._credits.append(entity)
        else:
            self._credits.append({"Entity": entity, "Reason": reason})

    @property
    def prefix(self):
        return self.command_prefix

    @property
    def credits(self):
        return self._credits

    async def get_context(self, msg, *, cls=EmbedContext):
        return await super().get_context(msg, cls=cls)

class NeoBot(NeoBase):
    TYPO_DISTANCE: ClassVar[int] = 5

    def setup(self) -> None:
        self.add_cog(TypoSuggest(self, distance_func=similarity_func_factory(self.TYPO_DISTANCE), cache=LRUCache(2048), detect_sub_cmd_typo=True))

    async def on_command_error(self, ctx: EmbedContext, error: CommandError):
        # return if already handled by the command's
        # error handler
        if hasattr(error, "handled"):
            return

        if isinstance(error, CommandNotFound):
            return

        if isinstance(error, DisabledCommand):
            async with ctx.std_embed() as em:
                em.title = get_emoji("CAUTION") + " | Command Disabled"
                em.description = f"The `{ctx.command}` command has currently beem disabled for maintenance purposes"
                error.handled = True
            return
        if isinstance(error, CheckFailure):
            if isinstance(error, NoPrivateMessage):
                async with ctx.std_embed() as em:
                    em.title = get_emoji("NO", 1) + " | Command not available in DMs"
                    em.description = f"The `{ctx.command}` command cannot be used in private channels with the bot at the moment"
                    em.set_footer(text="I appreciate you sneaking into my DMs tho :D")
                    error.handled = True
                return
            if isinstance(error, NotOwner):
                async with ctx.std_embed() as em:
                    em.title = get_emoji("DENIED") + " | Owner only Command"
                    em.description = f"The `{ctx.command}` command can only be used by the bot owner(s)"
                    em.set_footer(text="Stop trying to hack me already smh")
                    error.handled = True
                return
            if isinstance(error, MissingPermissions):
                async with ctx.std_embed() as em:
                    em.title = get_emoji("NO", 1) + " | Missing Permissions"
                    singular = bool(len(error.missing_perms) - 1)
                    em.description = (
                        (f"You don't possess the required permissions to use the `{ctx.command}` command\n"
                        "The permission" + "s" * singular + " you're missing"
                        " " + ("is", "are")[singular] + ":\n")
                        + "```\n"
                        + ("\n".join(i.replace("_", " ") for i in error.missing_perms))
                        + "\n```")
                    error.handled = True
                return
            if isinstance(error, BotMissingPermissions):
                em = ctx.std_embed()
                em.title = get_emoji("NO", 1) + " | Bot Missing Permissions"
                singular = bool(len(error.missing_perms) - 1)
                em.description = (
                    (f"I don't possess the required permissions to execute the `{ctx.command}` command\n"
                    "The permission" + "s" * singular + " I am missing"
                    " " + ("is", "are")[singular] + ":\n")
                    + "```\n"
                    + ("\n".join(i.replace("_", " ") for i in error.missing_perms))
                    + "\n```")
                if not any(perm == "send_messages" or perm == "embed_links" for perm in error.missing_perms):
                    async with em:
                        error.handled = True
                        return
                else:
                    await em.send(ctx.author)
                    error.handled = True
                    return

            if isinstance(error, NSFWChannelRequired):
                async with ctx.std_embed() as em:
                    em.title = get_emoji("NSFW") + " | NSFW Command"
                    em.description = f"Hold your horses, the `{ctx.command}` command can only be used in NSFW marked channels"
                    error.handled = True
                return

            async with ctx.std_embed() as em:
                logger.warning("Undefined CheckFailure Exception encountered of type %s. error: %s", type(error), error)
                em.title = get_emoji("DENIED") + " | Can't use Command"
                em.description = f"You don't have sufficient discord privileges to use this command"
                em.set_footer(text="Contact my developer(s) to help make this message clearer")
            return

        if isinstance(error, CommandInvokeError):
            cause = CommandInvokeError.__cause__
            if isinstance(cause, HTTPException):
                em = ctx.std_embed()
                em.title = get_emoji("SAD", 2) + " | Error while executing command"
                em.description = "An error occurred while sending the result" \
                    f"\nFailed with error code `{error.__cause__.code}` and status code `{error.__cause__.status}`" + \
                    "\n\nThe error desciption from discord was:\n" + \
                    '`' + cause.text + '`'
                await em.send(ctx.author)
                error.handled = True
                cause.handled = True
                return
        try:
            async with ctx.std_embed() as em:
                em.title = get_emoji("SAD", 2) + " | Unexpected Error"
                em.description = f"An unexpected error occurred in the `{ctx.command}` command, I have informed my developer(s)" \
                    " of the error."
                error.handled = True
            logger.critical("An unexpected command error occured!", exc_info=error)
        except:
            logger.exception("An exception occurred while handling a command error")

    async def on_error(self, event_method, *args, **kwargs):
        if hasattr(event_method, "handled"):
            return
        logger.error(event_method, exc_info=event_method)

    async def on_command_typo(self, ctx: EmbedContext, typo: TypoSuggestion):
        if typo.get_best()[0] > self.TYPO_DISTANCE:
            return

        sub_cmd = not (typo.parent is self)
        async with ctx.std_embed() as em:
            em.delete_after = 10
            _cmd = (("sub" * sub_cmd) + "command")
            par_name = getattr(typo.parent, 'qualified_name', '')
            em.title = get_emoji("PUZZLED") + " | " + _cmd.title() + " Not Found"
            em.description = ("The " + _cmd + " "
                + "`" + par_name + (' ' * sub_cmd) + typo.typo + "`"
                + " was not found, maybe you meant:\n"
                + "```\n" + "\n".join(i for i in map(lambda tr: par_name + " " + tr[1], typo.get_top(3))) + "```")
            em.set_footer(text="Did I wrongly report this as a command typo? If yes, Report it please.")
