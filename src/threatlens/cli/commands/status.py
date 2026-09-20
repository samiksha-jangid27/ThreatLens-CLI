from rich.console import Console

console = Console()


def status() -> None:
    """Display ThreatLens system status."""
    console.print("[bold green]ThreatLens[/bold green] is ready.")
