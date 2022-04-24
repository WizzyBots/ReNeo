from __future__ import annotations

import traceback
from io import StringIO
from typing import TYPE_CHECKING

from discord.ext.commands.core import bot_has_permissions, is_owner
from discord.ext.commands.errors import CommandRegistrationError, ExtensionAlreadyLoaded
from disctools.abstractions import Cog
from disctools.commands import CCmd, Command, inject
from neobot.core.utils import get_emoji
from neobot.core.utils.context import EmbedContext # dpy needs this during runtime *sigh*

# WARNING: Extremely Junky WET code ahead

class Management(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.cmds = {}
        self.cogs = {}

    @is_owner()
    @bot_has_permissions(send_messages=True, embed_links=True)
    @inject(name="load", aliases=["reload"], case_insensitive=True)
    class Load(CCmd):
        cog: Management

        async def main(self, ctx: EmbedContext, *Names: str):
            names = list(Names)
            bot = self.cog.bot
            done = ""
            failed = 0
            extended_once = False

            for name in names:
                if name == "~" and not extended_once:
                    names.extend(bot.extensions)
                    extended_once = True
                    continue
                try:
                    bot.load_extension(name)
                    done += (f"{get_emoji('YES')} | Loaded {name}\n")
                except ExtensionAlreadyLoaded:
                    bot.reload_extension(name)
                    done += (f"{get_emoji('YES')} | Reloaded {name}\n")
                except Exception:
                    failed += 1
                    done += get_emoji("NO") + " | Failed to Load " + name + "\n"
                    with StringIO() as fp:
                        traceback.print_exc(file=fp)
                        async with ctx.std_embed(title=f"{get_emoji('IMP')} | Cannot Load Extension {name}") as em:
                            em.description = (f"Failed to load extension `{name}`\n```py\n{fp.getvalue()}```")

            await self.cog.send_load_res(ctx, bool(len(names)), failed, len(names), "Extension", done)


        @bot_has_permissions(embed_links=True, send_messages=True)
        @inject(name="cmd", aliases=["command", "commands"])
        class Cmd(Command):
            async def main(self, ctx: EmbedContext, *names):
                done = ""
                failed = 0

                for name in names:
                    try:
                        self.parent.cog.load_cmd(name)
                        done += (f"{get_emoji('YES')} | Loaded {name}\n")
                    except (ValueError, CommandRegistrationError):
                        try:
                            self.parent.cog.reload_cmd(name)
                            done += (f"{get_emoji('YES')} | Reloaded {name}\n")
                        except ValueError:
                            failed += 1
                            done += get_emoji("NO") + " | Failed to Load " + name + "\n"
                            with StringIO() as fp:
                                traceback.print_exc(file=fp)
                                async with ctx.std_embed(title=f"{get_emoji('IMP')} | Cannot Load Command {name}") as em:
                                    em.description = (f"Failed to load command `{name}`\n```py\n{fp.getvalue()}```")

                await self.parent.cog.send_load_res(ctx, bool(len(names)), failed, len(names), "Command", done)

        @bot_has_permissions(embed_links=True, send_messages=True)
        @inject(name="cog", aliases=["cogs"])
        class _Cog(Command):
            async def main(self, ctx: EmbedContext, *names):
                done = ""
                failed = 0

                for name in names:
                    try:
                        self.parent.cog.load_cog(name)
                        done += (f"{get_emoji('YES')} | Loaded {name}\n")
                    except (ValueError, CommandRegistrationError):
                        try:
                            self.parent.cog.reload_cog(name)
                            done += (f"{get_emoji('YES')} | Reloaded {name}\n")
                        except ValueError:
                            failed += 1
                            done += get_emoji("NO") + " | Failed to Load " + name + "\n"
                            with StringIO("w+") as fp:
                                traceback.print_exc(file=fp)
                                async with ctx.std_embed(title=f"{get_emoji('IMP')} | Cannot Load Cog {name}") as em:
                                    em.description = (f"Failed to load cog `{name}`\n```py\n{fp.getvalue()}```")

                await self.parent.cog.send_load_res(ctx, bool(len(names)), failed, len(names), "Cog", done)

    @is_owner()
    @bot_has_permissions(send_messages=True, embed_links=True)
    @inject(name="unload", case_insensitive=True)
    class Unload(CCmd):
        async def main(self, ctx: EmbedContext, *Names: str):
            names = list(Names)
            bot = self.cog.bot
            failed = 0
            done = ""
            extended_once = False

            for name in names:
                if name == "~" and not extended_once:
                    names.extend(bot.extensions)
                    extended_once = True
                    continue
                try:
                    bot.unload_extension(name)
                    done += (f"{get_emoji('YES')} | Unloaded {name}\n")
                except Exception:
                    failed += 1
                    done += get_emoji("NO") + " | Failed to Unload " + name + "\n"
                    with StringIO() as fp:
                        traceback.print_exc(file=fp)
                        async with ctx.std_embed(title=f"{get_emoji('IMP')} | Cannot Unload Extension {name}") as em:
                            em.description = (f"Failed to unload extension `{name}`\n```py\n{fp.getvalue()}```")

            await self.cog.send_load_res(ctx, bool(len(names)), failed, len(names), "Extension", done, True)

        @bot_has_permissions(embed_links=True, send_messages=True)
        @inject(name="cmd", aliases=["command", "commands"])
        class Cmd(Command):
            async def main(self, ctx: EmbedContext, *names):
                done = ""
                failed = 0

                for name in names:
                    try:
                        self.parent.cog.unload_cmd(name)
                        done += (f"{get_emoji('YES')} | Unloaded {name}\n")
                    except (ValueError, CommandRegistrationError):
                        failed += 1
                        done += get_emoji("NO") + " | Failed to Unload " + name + "\n"
                        with StringIO() as fp:
                            traceback.print_exc(file=fp)
                            async with ctx.std_embed(title=f"{get_emoji('IMP')} | Cannot Unload Command {name}") as em:
                                em.description = (f"Failed to unload command `{name}`\n```py\n{fp.getvalue()}```")

                await self.parent.cog.send_load_res(ctx, bool(len(names)), failed, len(names), "Command", done, True)

        @bot_has_permissions(embed_links=True, send_messages=True)
        @inject(name="cog", aliases=["cogs"])
        class _Cog(Command):
            async def main(self, ctx: EmbedContext, *names):
                done = ""
                failed = 0

                for name in names:
                    try:
                        self.parent.cog.unload_cog(name)
                        done += (f"{get_emoji('YES')} | Unloaded {name}\n")
                    except (ValueError, CommandRegistrationError):
                        failed += 1
                        done += get_emoji("NO") + " | Failed to Unload " + name + "\n"
                        with StringIO() as fp:
                            traceback.print_exc(file=fp)
                            async with ctx.std_embed(title=f"{get_emoji('IMP')} | Cannot Unload Cog {name}") as em:
                                em.description = (f"Failed to unload cog `{name}`\n```py\n{fp.getvalue()}```")

                await self.parent.cog.send_load_res(ctx, bool(len(names)), failed, len(names), "Cog", done, True)

    async def send_load_res(self, ctx: EmbedContext, plural: bool, failed: int, total: int, obj: str, done: str, unload: bool = False):
        async with ctx.std_embed() as em:
            load_str = (("un" * unload) + "loaded ").title()
            if not failed:
                em.title = get_emoji("YES") + " | Successfully " + load_str + ("all " * plural) + obj + ("s" * plural)
            else:
                em.title = get_emoji("CAUTION") + f" | {load_str} {total - failed} {obj}s of {total}"
            em.description = "```\n" + done + "```"

    def reload_cmd(self, name: str, strict: bool = True):
        bot = self.bot
        cmd = bot.get_command(name)
        if not cmd and strict:
            raise ValueError(f"No command exists by the name of {name}")
        bot.remove_command(cmd.name) # Remove all aliases
        bot.add_command(cmd)

    def unload_cmd(self, name: str, strict: bool = True):
        cmd = self.bot.remove_command(name)
        if not cmd and strict:
            raise ValueError(f"No command exists by the name of {name}")
        if cmd:
            self.cmds[name] = cmd

    def load_cmd(self, name: str, strict: bool = True):
        bot = self.bot
        cmd = self.cmds.pop(name, None)
        if not cmd and strict:
            raise ValueError(f"No command/alias named {name} found")
        if cmd:
            bot.remove_command(cmd.name)
            bot.add_command(cmd)

    def reload_cog(self, name: str, strict: bool = True):
        bot = self.bot
        cog = bot.remove_cog(name)
        if not cog and strict:
            raise ValueError(f"No cog exists by the name of {name}")
        bot.add_cog(cog)

    def unload_cog(self, name: str, strict: bool = True):
        cog = self.bot.remove_cog(name)
        if not cog and strict:
            raise ValueError(f"No cog exists by the name of {name}")
        if cog:
            self.cogs[name] = cog

    def load_cog(self, name: str, strict: bool = True):
        bot = self.bot
        cog = self.cogs.pop(name, None)
        if not cog and strict:
            raise ValueError(f"No cog named {name} found")
        if cog:
            bot.remove_cog(cog.name)
            bot.add_cog(cog)


def setup(bot):
    bot.add_cog(Management(bot))
