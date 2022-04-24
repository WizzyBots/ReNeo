"""Package for cog, command utils"""
from .text import Text

def setup(bot):
    bot.add_cog(Text())
