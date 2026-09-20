import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.repositories import IncidentRepository


console = Console()


def _get_repository() -> IncidentRepository:
    """Create the default ThreatLens incident repository."""

    database_path = Path.home() / ".threatlens" / "threatlens.db"
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return IncidentRepository(
        ThreatLensDatabase(database_path)
    )


def incidents(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output incidents as JSON.",
    ),
) -> None:
    """List stored ThreatLens incidents."""

    repository = _get_repository()
    records = repository.list_all()

    if json_output:
        payload = {
            "incidents": records,
            "count": len(records),
        }

        print(
            json.dumps(
                payload,
                indent=2,
            )
        )
        return

    if not records:
        console.print(
            "[yellow]No incidents recorded.[/yellow]"
        )
        return

    table = Table(
        title="ThreatLens Incidents"
    )

    table.add_column("ID", justify="right")
    table.add_column("Timestamp")
    table.add_column("Risk", justify="right")
    table.add_column("Severity")
    table.add_column("Status")

    for incident in records:
        status = (
            "SUSPICIOUS"
            if incident["is_suspicious"]
            else "OBSERVATION"
        )

        table.add_row(
            str(incident["id"]),
            incident["timestamp"],
            f'{incident["risk_score"]:.0f}',
            incident["severity"],
            status,
        )

    console.print(table)