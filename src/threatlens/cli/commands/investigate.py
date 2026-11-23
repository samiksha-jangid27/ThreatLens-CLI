import typer
from rich.console import Console
from rich.panel import Panel

from threatlens.cli.errors import handle_errors
from threatlens.config import database_path
from threatlens.detection.investigation import (
    IncidentInvestigator,
)
from threatlens.explainability.explainer import (
    ThreatExplainer,
)
from threatlens.storage.database import (
    ThreatLensDatabase,
)
from threatlens.storage.repositories import (
    IncidentRepository,
)

console = Console()


def _get_repository() -> IncidentRepository:
    """Create the default ThreatLens incident repository."""

    return IncidentRepository(ThreatLensDatabase(database_path()))


@handle_errors
def investigate(
    incident_id: int = typer.Argument(
        ...,
        help="ID of the incident to investigate.",
    ),
) -> None:
    """Investigate a stored ThreatLens incident."""

    repository = _get_repository()

    incident = repository.get(incident_id)

    if incident is None:
        console.print(f"[red]Incident #{incident_id} not found.[/red]")
        raise typer.Exit(code=1)

    investigation = IncidentInvestigator().investigate(incident)

    explanation = incident.get("explanation") or ThreatExplainer().explain(
        {
            "signals": incident.get(
                "signals",
                {},
            ),
            "risk": {
                "risk_score": incident["risk_score"],
                "severity": incident["severity"],
            },
        }
    )

    console.print(
        Panel(
            f"[bold]Incident:[/bold] "
            f"#{investigation['incident_id']}\n"
            f"[bold]Risk Score:[/bold] "
            f"{investigation['risk_score']:.0f}/100\n"
            f"[bold]Severity:[/bold] "
            f"{investigation['severity']}\n"
            f"[bold]Priority:[/bold] "
            f"{investigation['priority']}\n"
            f"[bold]Status:[/bold] "
            f"{investigation['status']}",
            title="ThreatLens Investigation",
        )
    )

    console.print("\n[bold]Triggered Signals[/bold]")

    if investigation["triggered_signals"]:
        for signal in investigation["triggered_signals"]:
            console.print(f"  [red]●[/red] {signal}")
    else:
        console.print("  [green]No anomalous signals[/green]")

    console.print("\n[bold]Behavioral Evidence[/bold]")

    if explanation["evidence"]:
        for evidence in explanation["evidence"]:
            console.print(f"  [yellow]→[/yellow] {evidence['description']}")
    else:
        console.print("  [green]No additional evidence available.[/green]")

    console.print("\n[bold]Recommendation[/bold]")

    console.print(f"  {investigation['recommendation']}")
