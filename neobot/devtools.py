from os import system
from pathlib import Path
from sys import platform, executable, version_info
import venv as Venv

from typer import Typer, Argument, Context
import typer

app = Typer()

venv_path = None
name = ""

@app.callback()
def callback(venv: str = typer.Option(".venv", help="name of the venv folder in the cwd")):
    global venv_path
    global name

    name = venv
    if version_info < (3, 8):
        exit("NeoBot requires python38+")

    if not executable:
        exit("Unable to determine python executable path")

    root = Path.cwd().absolute()
    if platform.startswith("linux") or platform.startswith("darwin"):
        venv_path = root / venv / "bin" / "python"
    elif platform.startswith("win"):
        venv_path = root / venv / "Scripts" / "python.exe"
    else:
        exit("Unsupported Platform")

    if not venv_path.exists():
        typer.echo(typer.style(f"folder \'{venv}\' doesn't exit", fg=typer.colors.BRIGHT_MAGENTA))
        typer.Abort()

# Not tested or created with non-windows platforms in mind for now

@app.command("clearenv", help="Reset the venv (remove all installed libs)")
def resetvenv():
    Venv.create(name, clear=True, with_pip=True)

@app.command(context_settings={"allow_extra_args": True})
def update(ctx: Context, args: str = Argument(..., help="Name of packages to update")):
    pkgs = ctx.args + [args]
    system(f"{venv_path} -m poetry update " + " ".join(pkgs))

@app.command(help="Install neobot")
def install():
    system(f"{venv_path} -m poetry install -E web")

@app.command(help="Install all dependencies in the venv")
def setup():
    system(f"{venv_path} -m pip install -U poetry")
    install()

@app.command(help="Run neobot in dev mode")
def run():
    system(f"{venv_path} -m neobot run --dev")

app.command("resetvenv", help="Reset the venv and set it up again")(lambda: (resetvenv(), setup()))

if __name__ == "__main__":
    app()