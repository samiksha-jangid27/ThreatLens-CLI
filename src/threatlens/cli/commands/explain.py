import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

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

    database_path = (
        Path.home()
        / ".threatlens"
        / "threatlens.db"
    )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return IncidentRepository(
        ThreatLensDatabase(database_path)
    )


def explain(
    incident_id: int = typer.Argument(
        ...,
        help="ID of the incident to explain.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output explanation as JSON.",
    ),
) -> None:
    """Explain why a ThreatLens incident was flagged."""

    repository = _get_repository()

    incident = repository.get(
        incident_id
    )

    if incident is None:
        console.print(
            f"[red]Incident #{incident_id} not found.[/red]"
        )
        raise typer.Exit(code=1)

    explanation = ThreatExplainer().explain(
        {
            "signals": incident.get(
                "signals",
                {},
            ),
            "risk": {
                "risk_score": incident[
                    "risk_score"
                ],
                "severity": incident[
                    "severity"
                ],
            },
        }
    )

    if json_output:
        print(
            json.dumps(
                {
                    "incident_id": incident[
                        "id"
                    ],
                    **explanation,
                },
                indent=2,
            )
        )
        return

    console.print(
        Panel(
            f"[bold]Incident:[/bold] "
            f"#{incident['id']}\n"
            f"[bold]Risk Score:[/bold] "
            f"{incident['risk_score']:.0f}/100\n"
            f"[bold]Severity:[/bold] "
            f"{incident['severity']}\n"
            f"[bold]Evidence Count:[/bold] "
            f"{explanation['evidence_count']}",
            title="ThreatLens Explanation",
        )
    )

    console.print(
        "\n[bold]Why Was This Incident Flagged?[/bold]"
    )

    if not explanation["evidence"]:
        console.print(
            "  [green]No anomalous behavioral evidence identified.[/green]"
        )
    else:
        for evidence in explanation["evidence"]:
            console.print(
                f"  [red]●[/red] "
                f"{evidence['description']}"
            )

            details = evidence.get(
                "details",
                {},
            )

            anomalous_features = details.get(
                "anomalous_features"
            )

            if anomalous_features:
                console.print(
                    "    [bold]Features:[/bold] "
                    + ", ".join(
                        anomalous_features
                    )
                )

            triggered_signals = details.get(
                "triggered_signals"
            )

            if isinstance(
                triggered_signals,
                dict,
            ) and triggered_signals:
                console.print(
                    "    [bold]Triggered changes:[/bold] "
                    + ", ".join(
                        triggered_signals.keys()
                    )
                )

    console.print(
        "\n[bold]Summary[/bold]"
    )

    console.print(
        f"  {explanation['summary']}"
    )
