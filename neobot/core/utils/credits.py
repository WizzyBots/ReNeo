from typing import Dict, List, Optional, Union, TypeVar
from discord import Embed

from .emoji import get_emoji
from .context import NeoEmbed as Emb

__all__ = ['Credits', 'CreditEntry', 'format_cred', 'embed_creds']

Credits = List[Union[Dict[str, str], str]]
CreditEntry = Union[Dict[str, str], str]

T = TypeVar("T", bound=Embed)


def format_cred(entry: CreditEntry) -> str:
    """Return a string which can be put in an embed field

    Parameters
    ----------
    entry : Union[Dict[str, str], str]
        A dict or a str.

    Returns
    -------
    str
        The formatted string
    """
    if isinstance(entry, dict):
        return f"**{entry['Entity']}**\n{entry['Reason']}\n"
    return f"**{entry}**\n"


def embed_creds(_credits: Credits, embed: Optional[T] = None) -> T:
    if embed is None:
        embed = Emb()
    body = ""
    for i in _credits:
        body += format_cred(i)
    embed.description = body
    embed.title = get_emoji("SMILE", 1) +" | Credits"
    return embed
