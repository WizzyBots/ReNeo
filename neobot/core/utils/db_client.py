from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING
import asyncpg

from .db_abc import db_client, DbClientABC

if TYPE_CHECKING:
    from discord.guild import Guild

__all__ = (
    "PgClient",
)

@db_client("Postgre")
class PgClient(DbClientABC):
    def __init__(self, dns) -> None:
        self.pool: asyncpg.pool.Pool = asyncpg.create_pool(dns)
        self.append = (
            "UPDATE prefix "
            "SET prefix = prefix || $1 "
            "WHERE gid = $2"
            )
        self.get = "SELECT prefix FROM prefix WHERE gid = $1"
        self.set = "UPDATE prefix SET prefix = $1 WHERE gid = $2"
        self.create_table = \
            "CREATE TABLE IF NOT EXIST prefix (gid BIGINT NOT NULL CHECK (gid >= 0), prefix TEXT ARRAY)"

    async def get_prefix(self, guild: Guild) -> Optional[List[str]]:
        try:
            return (await self.pool.fetchrow(self.get, guild.id))["prefix"] # type: ignore[index]
        except Exception:
            return None

    async def load(self) -> Dict[int, List[str]]:
        async with self.pool.acquire() as con:
            return {
                    i[0]: i[1] async for i in con.cursor(f"SELECT * FROM prefix")
                }

    async def set_prefix(self, guild: Guild, prefixes: List[str]):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute(self.set, prefixes, guild.id)

    async def append_prefix(self, guild: Guild, prefix: str):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute(self.append, prefix, guild.id)

    async def create_prefix_table(self):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute(self.table)
