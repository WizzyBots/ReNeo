from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Awaitable, Dict, List, Union

import discord

if TYPE_CHECKING:
    from discord import Client, Guild, Message

    from .db_abc import DbClientABC

__all__ = (
    "PrefixManager",
)

class PrefixManager:
    """A manager for guild prefixes

    Note
    ----
    This is an async class.
    """
    async def __new__(cls, *args, **kw):
        self = super().__new__(cls)
        await self.__init__(*args, **kw)
        return self

    async def __init__(self, prefix_default: Union[List[str], str], bot: Client, db_client: DbClientABC, *, warm_cache: bool = False) -> None: # type: ignore
        # This dict is for reads. We write to the Db for persistence
        self._prefixes: Dict[int, List[str]] = {}
        if warm_cache:
            self._prefix = await db_client.load()
        self.bot = bot
        self.db = db_client
        user_id = self.bot.user.id
        self._mentions = [f'<@!{user_id}> ', f'<@{user_id}> ']
        self.pre_default: List[str] = prefix_default if isinstance(prefix_default, list) else [prefix_default]
        self.default = self._mentions + self.pre_default

    def __getitem__(self, guild: Guild) -> List[str]:
        # Modifying via this is not persistent
        # i.e prefix[guild].append("&") is not updated in DB
        return self._prefixes[guild.id]

    def __setitem__(self, guild: Guild, prefixes: List[str]) -> None:
        # await f[4] = ["5"] # is not possible!!!
        self.set_local_prefix(guild, prefixes)

    async def __call__(self, _, msg: Message):
        return await self.get_prefix(msg.guild)

    def __repr__(self) -> str:
        return f"<PrefixManager of {repr(self.bot)}>"

    @property
    def prefix(self) -> Dict[int, List[str]]:
        return self._prefixes

    ## Getters ##
    async def get_prefix(self, guild: Guild) -> List[str]:
        if not guild:
            return self.default
        prefixes = self._prefixes.get(guild.id, None)
        if prefixes:
            return prefixes + self._mentions
        prefixes = await self.db.get_prefix(guild)
        if prefixes:
            self._prefix[guild.id] = prefixes
            return prefixes + self._mentions
        return self.default

    def get_local_prefix(self, guild: Guild) -> List[str]:
        if not guild:
            return self.default # dm
        prefixes = self._prefixes.get(guild.id, None)
        if not prefixes:
            return self.default
        return prefixes + self._mentions

    def get_raw_prefix(self, guild: Guild) -> List[str]:
        return self._prefixes.get(guild.id, self.pre_default)

    ## Setters ##
    def set_local_prefix(self, guild: Guild, prefixes: List[str]) -> None:
        if not guild:
            raise TypeError(f"Expected discord.Guild, instead got {type(guild)}")
        self._prefixes[guild.id] = prefixes
        return None

    async def set_prefix(self, guild: Guild, prefixes: List[str]) -> None:
        self.set_local_prefix(guild, prefixes)
        await self.db.set_prefix(guild, prefixes)
        return None

    ## Modifiers ##
    def append_local_prefix(self, guild: Guild, prefix: str) -> None:
        if not guild:
            raise TypeError(f"Expected discord.Guild, instead got {type(guild)}")
        if guild.id not in self._prefixes:
            raise ValueError(f"No guild prefix record found with id: {guild.id}")
        else:
            self._prefixes[guild.id].append(prefix)
        return None

    async def append_prefix(self, guild: Guild, prefix: str) -> None:
        if guild.id not in self._prefixes:
            await self.set_prefix(guild, self.pre_default + [prefix])
        else:
            self.append_local_prefix(guild, prefix)
            await self.db.append_prefix(guild, prefix)
        return None

    ## task Methods ##
    # I have No idea, if I will ever use them
    # But, I will still make it!
    def append_prefix_task(self, guild: Guild, prefix: str) -> Awaitable[None]:
        if guild.id not in self._prefixes:
            task = asyncio.create_task(self.set_prefix(guild, self.pre_default + [prefix]))
        else:
            self.set_local_prefix(guild, [prefix])
            task = asyncio.create_task(self.db.append_prefix(guild, prefix))
        return task

    def set_prefix_task(self, guild: Guild, prefixes: List[str]) -> Awaitable[None]:
        self.set_local_prefix(guild, prefixes)
        return asyncio.create_task(self.db.set_prefix(guild, prefixes))
