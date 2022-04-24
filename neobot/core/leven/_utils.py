from inspect import isawaitable
from typing import Awaitable, TypeVar, Union, overload

T = TypeVar("T")

__all__ = ("maybe_awaitable",)

# For Some reason this overload fixes mypy
@overload
async def maybe_awaitable(obj: None) -> None:
    ...

@overload
async def maybe_awaitable(obj: Union[T, Awaitable[T]]) -> T:
    ...

async def maybe_awaitable(obj):
    if isawaitable(obj):
        return await obj
    else:
        return obj
