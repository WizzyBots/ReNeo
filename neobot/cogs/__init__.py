"""A package which is a discord extension."""
from .text import setup as text_setup
from .misc import setup as misc_setup

def setup(bot):
    text_setup(bot)
    misc_setup(bot)