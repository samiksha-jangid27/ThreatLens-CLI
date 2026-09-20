import typer

from threatlens.cli.commands.status import status
from threatlens.cli.commands.version import version

app = typer.Typer(
    name="threatlens",
    help="AI-powered behavioral threat detection CLI.",
)

app.command()(version)
app.command()(status)


if __name__ == "__main__":
    app()
