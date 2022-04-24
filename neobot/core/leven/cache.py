from __future__ import annotations

from collections import OrderedDict
from collections.abc import Hashable
from typing import Awaitable, Dict, Generic, Tuple, TypeVar, Optional, Union, overload
from abc import ABC, abstractmethod

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

T = TypeVar("T")

__all__ = (
    "Cache",
    "LRUCache",
    "CacheABC"
)

class CacheABC(Generic[K, V], ABC):
    @overload
    @abstractmethod
    def get(self, key: K) -> Union[Optional[V], Awaitable[Optional[V]]]:
        ...

    @overload
    @abstractmethod
    def get(self, key: K, default: T) -> Union[Union[V, T], Awaitable[Union[V, T]]]:
        ...

    @abstractmethod
    def get(self, key: K, default: T = None) -> Union[Union[Optional[V], T], Awaitable[Union[Optional[V], T]]]:
        """Can be overridden as an async method."""
        return NotImplemented

    @abstractmethod
    def put(self, key: K, value: V) -> None:
        """Can be overridden as an async method."""
        return None

class Cache(CacheABC[K, V]):
    def __init__(self) -> None:
        self._cache: Dict[K, V] = dict()

    @overload
    def get(self, key: K) -> Optional[V]:
        ...

    @overload
    def get(self, key: K, default: T) -> Union[V, T]:
        ...

    def get(self, key: K, default: Optional[T] = None) -> Union[Optional[V], T]:
        return self._cache.get(key, default)

    def put(self, key: K, value: V) -> None:
        self._cache[key] = value
        return None

    @overload
    def pop(self, key: K) -> Optional[V]:
        ...

    @overload
    def pop(self, key: K, default: T) -> Union[V, T]:
        ...

    def pop(self, key: K, default: Optional[T] = None) -> Union[Optional[V], T]:
        return self._cache.pop(key, default)

    def popitem(self) -> Tuple[K, V]:
        return self._cache.popitem()

    def clear(self) -> None:
        self._cache.clear()

class LRUCache(Cache[K, V]):
    def __init__(self, maxsize: Optional[int] = None) -> None:
        if isinstance(maxsize, int):
            maxsize = max(maxsize, 0)
        else:
            maxsize = None
        self.maxsize = maxsize
        self._cache: OrderedDict[K, V] = OrderedDict()

    @overload
    def peek(self, key: K) -> Optional[V]:
        ...

    @overload
    def peek(self, key: K, default: T) -> Union[V, T]:
        ...

    def peek(self, key: K, default: Optional[T] = None) -> Union[V, Optional[T]]:
        return self._cache.get(key, default)

    def get(self, key, default = None):
        try:
            self._cache.move_to_end(key, last=False)
        except KeyError:
            return default
        else:
            return self._cache[key]

    def put(self, key: K, value: V) -> None:
        super().put(key, value)
        if self.maxsize is not None:
            if len(self._cache) > self.maxsize:
                self._cache.popitem()
