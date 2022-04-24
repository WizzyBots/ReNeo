from __future__ import annotations
from re import L

from typing import List, Type, Union

from discord import AllowedMentions, File, Colour, Message
from discord.abc import User, Messageable
from discord.embeds import Embed, _EmptyEmbed, EmptyEmbed
from discord.ext.commands import Context

__all__ = ['DARK_SECONDARY_BG', 'DiscordColour', 'OptionalEmbedStr', 'NeoEmbed', 'EmbedContext']

DARK_SECONDARY_BG = int("2f3136", 16)

send_args = Context.send.__code__.co_varnames[1: Context.send.__code__.co_argcount]

DiscordColour = Union[int, Colour, _EmptyEmbed]
OptionalEmbedStr = Union[str, _EmptyEmbed]

class _SendingContext:
    def __init__(self, emb: NeoEmbed) -> None:
        self.emb = emb

    async def __aenter__(self) -> _SendingContext:
        if self.emb.ctx is None:
            raise ValueError("Expected Context object at embed.ctx got None")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.emb._validate_kwargs()
        self.emb.ctx.send(**self.emb.kwargs)

class NeoEmbed(Embed):
    def __init__(self, ctx: Context = None, **kwargs):
        self.ctx = ctx
        self.kwargs = {key: kwargs.get(key, None) for key in send_args if send_args != "tts"}
        self.kwargs["tts"] = bool(kwargs.get("tts", False))
        super().__init__(**kwargs)

    def setAuthor(self, author: User, *, url=EmptyEmbed):
        self.set_author(name=author.display_name, icon_url=author.avatar_url, url=url)

    @property
    def content(self):
        return self.kwargs["content"]

    @content.setter
    def content(self, val):
        self.kwargs["content"] = str(val)

    @property
    def tts(self):
        return self.kwargs["tts"]

    @tts.setter
    def tts(self, val):
        self.kwargs["tts"] = bool(val)

    @property
    def file(self):
        return self.kwargs["file"]

    @file.setter
    def file(self, val: File):
        self.kwargs["file"] = val

    @property
    def delete_after(self):
        return self.kwargs["delete_after"]

    @delete_after.setter
    def delete_after(self, val: float):
        self.kwargs["delete_after"] = val

    @property
    def nonce(self):
        return self.kwargs["nonce"]

    @nonce.setter
    def nonce(self, val: int):
        self.kwargs["nonce"] = val

    @property
    def allowed_mentions(self):
        return self.kwargs["allowed_mentions"]

    @allowed_mentions.setter
    def allowed_mentions(self, val: AllowedMentions):
        self.kwargs["allowed_mentions"] = val

    @property
    def files(self):
        return self.kwargs["files"]

    @files.setter
    def files(self, val: List[File]):
        self.kwargs["files"] = val

    @property
    def embed(self) -> Embed:
        return self.kwargs["embed"]

    @embed.setter
    def embed(self, val: Embed):
        self.kwargs["embed"] = val

    @property
    def embeds(self) -> List[Embed]:
        return self.kwargs["embeds"]

    @embeds.setter
    def embeds(self, val: List[Embed]):
        self.kwargs["embeds"] = val

    def sender(self) -> _SendingContext:
        return _SendingContext(self)

    async def __aenter__(self):
        if self.ctx is None:
            raise ValueError("Context must not be None when used in a with-statement!")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._validate_kwargs()
        if self.kwargs.get("mention_author", None) is None:
            self.kwargs["mention_author"] = False
        await self.ctx.reply(**self.kwargs)

    def _validate_kwargs(self):
        embed = self.kwargs.get("embed", None)
        embeds = self.kwargs.get("embeds", [])
        if embed and embeds:
            if embed in embeds:
                if not embed:
                    embeds.pop(embeds.index(embed))
                del self.kwargs["embed"]
            else:
                embeds.append(embed)
                del self.kwargs["embed"]
        if embed and not embeds:
            if self is not embed:
                embeds.extend((self, embed))
                del self.kwargs["embed"]
            else:
                pass
        if embeds and not embed:
            if self not in embeds:
                embeds.insert(0, self)
        if not (embed and embeds):
            self.kwargs["embed"] = self

    async def send(self, destination: Messageable) -> Message:
        if self.kwargs.get("embed", None) is None and self.kwargs.get("embeds", None) is None:
            self.kwargs["embed"] = self
        if not self.kwargs.get("embeds", None) is None:
            if not self in self.kwargs["embeds"]:
                self.kwargs["embeds"].append(self)
        return await destination.send(**self.kwargs)


class EmbedContext(Context):
    """A subclass with embeding utils"""
    @property
    def neo_embed(self) -> Type[NeoEmbed]:
        return NeoEmbed

    async def send_embed(self, content: str, title: OptionalEmbedStr = EmptyEmbed, colour: DiscordColour = EmptyEmbed, url: OptionalEmbedStr = EmptyEmbed) -> Message:
        return await self.send(embed=Embed(title=title, colour=colour, description=content, url=url))

    def std_embed(self, content: OptionalEmbedStr = EmptyEmbed, title: OptionalEmbedStr = EmptyEmbed, colour: DiscordColour = EmptyEmbed, url: OptionalEmbedStr = EmptyEmbed) -> NeoEmbed:
        """Return a standard embed

        Parameters
        ----------
        content : str
            The body of the embed
        title : Union[str, :class:`discord.colour._EmptyEmbed`], optional
            The embed title, by default EmptyEmbed
        colour :  Union[int, :class:`discord.Colour`, :class:`discord.colour._EmptyEmbed`], optional
            The embed colour, by default EmptyEmbed
        url : Union[str, :class:`discord.colour._EmptyEmbed`], optional
            Embed's url, by default EmptyEmbed

        Returns
        -------
        NeoEmbed
            The created embed.
        """
        embed = NeoEmbed(self, title=title, description=content, timestamp=self.message.created_at)
        embed.setAuthor(self.author)
        embed.colour = DARK_SECONDARY_BG
        return embed
