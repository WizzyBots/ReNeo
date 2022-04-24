from typing import Callable, Type

from discord.ext.commands import Converter, BadArgument
from discord.utils import maybe_coroutine

__all__ = (
    "convertor",
    "text_conv_factory",
    "DecStrConv",
    "BinaryStrConv",
    "HexStrConv",
    "InvalidInput"
)

def convertor(func: Callable) -> Type[Converter]:
    class c(Converter):
        async def convert(self, *args):
            return await maybe_coroutine(func, *args)

    c.__name__ = func.__name__
    return c

def text_conv_factory(name: str, mode: str) -> Type[Converter]:
    def x(_, content) -> str:
        return ' '.join((f"{x:{mode}}" for x in content.encode()))

    x.__name__ = name
    return convertor(x)

class InvalidInput(BadArgument):
    def __init__(self, argument):
        self.argument = argument
        super().__init__(f"Invalid parameter {argument}")

class StrConvType(type):
    def __new__(cls, name, bases, attrs, *, base: int = 10):
        klas = super().__new__(cls, name, bases, attrs)

        async def convert(self, ctx, arg: str) -> str:
            c = arg.replace(" ", "")
            try:
                temp = int(c, base)
                return temp.to_bytes((temp.bit_length() + 7) // 8, 'big').decode()
            except ValueError as err:
                raise InvalidInput(arg) from err

        # mypy raises an error here.
        klas.convert = convert # type: ignore
        return klas

class DecStrConv(Converter, metaclass=StrConvType):
    pass

class BinaryStrConv(DecStrConv, base=2): pass
class HexStrConv(DecStrConv, base=16): pass
