import asyncio
import logging
import sys
import time
from pathlib import Path
from enum import Enum
from typing import List, Optional

from neobot import NeoBot
from neobot.web import main as web_main
from neobot.devtools import app as tools

from typer import Typer, echo, Option, Abort, Argument

class ClockType(Enum):
    wall = "WALL"
    cpu = "CPU"

app = Typer()

app.add_typer(tools, name = "tools")

@app.command(name = "run", help = "Run neobot")
def main(token: str = Argument("")) -> int:
    from dotenv import load_dotenv
    load_dotenv()
    from os import getenv

    if not token:
        token = getenv("TOKEN") # type: ignore

        if token is None:
            print("No token provided")
            raise Abort()

    DB_DNS = getenv("DATABASE_URL")
    db_client = None
    if DB_DNS:
        from neobot.core.utils import PgClient
        db_client = PgClient(DB_DNS)

    if sys.version_info[0] ==  3 and sys.version_info[1] >=  8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logging.Formatter.converter = time.gmtime
    logging.basicConfig(format = "%(asctime)s %(name)s:%(levelname)s: %(message)s", level = logging.INFO, datefmt = "[%a, %d %B %Y %X]")
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)

    bot = NeoBot(",", db_client=db_client)
    bot.load_extension("neobot.cogs")
    web_main(bot)
    bot.run(token)
    return 0

@app.command(name = "profile", help = "Profile the bot with yappi")
def profile(token: str = Argument(""),
            clock_type: ClockType = Option("wall", "--clock", "-c", case_sensitive = False),
            load_path: Optional[List[Path]] = Option(
                None, "--load", "-l",
                exists = True,
                file_okay = True,
                dir_okay = False,
                writable = False,
                readable = True,
                resolve_path = True,
                allow_dash = True
            ),
            save_path: Optional[Path] = Option(
                None, "--save", "-s",
                file_okay = True,
                dir_okay = False,
                writable = True,
                readable = False,
                resolve_path = True,
                allow_dash = True
            ),
            print_results: bool = Option(True, "--print"),
            print_to: Optional[Path] = Option(
                None, "--print-to", "-pt",
                file_okay = True,
                dir_okay = False,
                writable = True,
                readable = False,
                resolve_path = True,
                allow_dash = True
            )
        ):
    try:
        import yappi
    except (ModuleNotFoundError, ImportError):
        echo("yappi profiler is not installed!")
        raise Abort()

    yappi.set_clock_type(clock_type.value)

    yappi.start()

    main(token)

    yappi.stop()

    stats = yappi.get_func_stats()

    if load_path is not None:
        stats.add(map(str, load_path))

    if print_results:
        out = sys.stdout
        if print_to is not None:
            try:
                out = print_to.open(mode="w")
            except:
                echo(f"Could Not print to {print_to} since the path does not exist!")
                raise
        stats.print_all(out=out)

    if save_path is not None:
        stats.save(str(save_path))

def App():
    import sys
    argv = []
    for i in sys.argv:
        if i not in {"-d", "--dev"}:
            argv.append(i)
    # print(sys.argv, argv)
    app(args=argv[1:], prog_name="neobot")

if __name__ == "__main__":
    App()
