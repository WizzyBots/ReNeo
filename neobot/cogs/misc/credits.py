from discord.ext.commands.core import bot_has_permissions
from disctools import Command
from neobot.core.utils import NeoEmbed
from neobot.core.utils.context import DARK_SECONDARY_BG
from neobot.core.utils.credits import embed_creds


@bot_has_permissions(send_messages=True, embed_links=True)
class _Credits(Command):
    def __init__(self, bot, **kwargs):
        super().__init__(func=None, **kwargs)
        self.embed = embed_creds(bot.credits, NeoEmbed(colour=DARK_SECONDARY_BG))

    async def main(self, ctx):
        self.embed.ctx = ctx
        async with self.embed:
            return

def setup(bot):
    bot.add_command(_Credits(bot, name="credits", aliases=["creds"]))
