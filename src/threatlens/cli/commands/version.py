from rich.console import Console

from threatlens import __version__

console = Console()


def version() -> None:
    """Display the ThreatLens version."""
    console.print(
        f"[bold cyan]ThreatLens[/bold cyan] v{__version__}"
    )
