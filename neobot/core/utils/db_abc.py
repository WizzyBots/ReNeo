from abc import abstractmethod, ABCMeta
from typing import Dict, List, Optional

from discord import Guild

## As 0f 2020 I only use the DB for prefixes
# If i expand upon the DB then I shall add more methods
#                    - Note To Self

# GOAL: [Make it easier to migrate to different DB
#        By Abstracting the DB specfic code]

def db_client(db_type: Optional[str] = None):
    def inner(cls):
        cls.__db_ver__ = 1
        cls.__db_type__ = db_type
        return cls
    return inner

@db_client(None)
class DbClientABC(metaclass=ABCMeta):
    @abstractmethod
    async def load(self) -> Dict[int, List[str]]:
        raise NotImplementedError

    @abstractmethod
    async def get_prefix(self, guild: Guild) -> Optional[List[str]]:
        """Gets the prefix associated with a Guild"""
        raise NotImplementedError

    @abstractmethod
    async def set_prefix(self, guild: Guild, prefixes: List[str]) -> None:
        """Sets the prefix for a Guild Object"""
        raise NotImplementedError

    @abstractmethod
    async def append_prefix(self, guild: Guild, prefix: str) -> None:
        """Appends the prefix"""
        raise NotImplementedError

    @abstractmethod
    async def create_prefix_table(self) -> None:
        """
        Create prefix table if not exists
        """
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, C: type):
        for i in C.__mro__:
            attrs = i.__dict__.keys()
            if attrs >= {"load", "set_prefix" , "append_prefix", "create_prefix_table"}:
                return True
        else:
            return NotImplemented
