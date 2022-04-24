from __future__ import annotations

from asyncio import create_task
from typing import Generator, TYPE_CHECKING, Callable, List, Optional, Tuple, Iterator

from discord.ext.commands.core import Group, _CaseInsensitiveDict
from discord.utils import get

from ._utils import maybe_awaitable

if TYPE_CHECKING:
    from discord.ext.commands import Context
    from discord.ext.commands.core import Command, GroupMixin

    from ..utils.types import AnyBot
    from .cache import CacheABC

__all__ = (
    "TypoSuggestion",
    "TypoClient"
)

class TypoSuggestion:
    suggestions: List[Tuple[int, str]]
    typo: str
    parent: GroupMixin

    def __init__(self, parent: GroupMixin, typo: Optional[str] = None, suggestions: Optional[List[Tuple[int, str]]] = None) -> None:
        if suggestions is None:
            suggestions = []
        if typo is None:
            typo = ""

        self.parent = parent
        self.typo = typo
        self.suggestions = suggestions

    def __getitem__(self, idx: int):
        return self.suggestions[idx]

    def __iter__(self) -> Iterator[Tuple[int, str]]:
        return iter(self.suggestions)

    def __len__(self) -> int:
        return len(self.suggestions)

    def __eq__(self, other) -> bool:
        return (other.parent == self.parent
            and other.typo == self.typo and isinstance(other, TypoSuggestion))

    def __ne__(self, other) -> bool:
        return (not isinstance(other, TypoSuggestion) or
            other.parent != self.parent or
            other.typo != self.typo)

    def __repr__(self) -> str:
        return f"<TypoSuggestion for '{getattr(self.parent, 'qualified_name', '') + ' ' + self.typo}'>"

    def __bool__(self) -> bool:
        return bool(self.typo and self.parent)

    def sort(self) -> None:
        self.suggestions.sort()

    def get_best(self) -> Tuple[int, str]:
        least = self.suggestions[0]
        for i in self.suggestions:
            if i < least:
                least = i

        return least

    def get_top(self, num: int) -> Generator[Tuple[int, str], None, None]:
        self.sort()
        yield from self.suggestions[:num]

    def get_top_within_threshold(self, threshold: int, num: int = 3) -> Generator[Tuple[int, str], None, None]:
        self.sort()
        elems = 0
        for i in self.suggestions:
            if elems >= num:
                break
            if i[0] > threshold:
                break
            yield i
            elems += 1

class TypoClient:
    def __init__(self, bot: AnyBot, distance_func: Callable[[str, str], int], cache: CacheABC = None) -> None:
        self.bot = bot
        self.dist = distance_func
        self.cache: Optional[CacheABC[Tuple[str, str], List[Tuple[int, str]]]] = cache

    @staticmethod
    def parse_content(ctx: Context) -> Optional[List[str]]:
        if not ctx.prefix:
            return None

        if ctx.invoked_with:
            if ctx.command is None:
                return [ctx.invoked_with]

            if isinstance(ctx.command, Group):
                if ctx.invoked_subcommand:
                    return None
                elif ctx.subcommand_passed is None:
                    return None

                cmds = ctx.invoked_parents.copy()
                cmds.append(ctx.subcommand_passed)
                return cmds

            return None
        return None

    def resolve_max(self, locator: Optional[List[str]]) -> Optional[Tuple[GroupMixin, Optional[str]]]:
        if not locator:
            return None

        par: GroupMixin = self.bot
        cmd: Optional[Command] = None

        for i in locator[:-1]:
            tmp = par.all_commands.get(i, None)

            if tmp is None:
                locator[-1] = i
                break

            par = tmp

        cmd = par.all_commands.get(locator[-1], None)

        if not cmd:
            return par, locator[-1]

        return cmd, None

    def _gen_suggests(self, par: Group, typo: str) -> List[Tuple[int, str]]:
        suggestions = []
        distance = self.dist

        if isinstance(par.all_commands, _CaseInsensitiveDict):
            typo = typo.casefold()

        for i in par.all_commands:
            suggestions.append((distance(typo, i), i))

        return suggestions

    async def generate_suggestions(self, par: GroupMixin, typo: Optional[str]) -> Optional[List[Tuple[int, str]]]:
        if not typo:
            return None

        # Use a tuple for string pigeonhole opts to work
        if self.cache is not None:
            cached: Optional[List[Tuple[int, str]]] = await maybe_awaitable(self.cache.get((str(par), typo)))
            if cached is not None and isinstance(cached, list):
                return cached.copy()

            suggest = self._gen_suggests(par, typo)

            # this might be a web request, we want sugestions to be responsive
            create_task(maybe_awaitable(self.cache.put((str(par), typo), suggest)))
            return suggest
        else:
            return self._gen_suggests(par, typo)

    async def process_typo(self, ctx: Context) -> Optional[TypoSuggestion]:
        loc = self.resolve_max(self.parse_content(ctx))

        if loc is None:
            return None

        return TypoSuggestion(*loc, await self.generate_suggestions(*loc))