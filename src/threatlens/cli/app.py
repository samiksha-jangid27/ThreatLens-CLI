import typer
from rich.console import Console

from threatlens.cli.commands.status import status

app = typer.Typer(
    name="threatlens",
    help="AI-powered behavioral threat detection CLI.",
)

console = Console()


@app.command()
def version() -> None:
    """Display the ThreatLens version."""
    console.print("[bold cyan]ThreatLens[/bold cyan] v0.1.0")


app.command(name="status")(status)


if __name__ == "__main__":
    app()