from .core.bot import NeoBase, NeoBot

from importlib.metadata import version

try:
    __version__ = version("neobot")
except:
    ...