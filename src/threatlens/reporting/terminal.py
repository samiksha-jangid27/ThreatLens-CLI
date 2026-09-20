from typing import Any

from rich.console import Console
from rich.table import Table


console = Console()


def print_terminal_report(
    incidents: list[dict[str, Any]],
) -> None:
    """
    Print a human-readable incident report.
    """

    if not incidents:
        console.print(
            "[yellow]No incidents recorded.[/yellow]"
        )
        return

    table = Table(
        title="ThreatLens Security Report"
    )

    table.add_column(
        "ID",
        justify="right",
    )
    table.add_column("Timestamp")
    table.add_column(
        "Risk",
        justify="right",
    )
    table.add_column("Severity")
    table.add_column("Status")

    for incident in incidents:
        status = (
            "SUSPICIOUS"
            if incident.get("is_suspicious")
            else "OBSERVATION"
        )

        table.add_row(
            str(incident["id"]),
            str(incident["timestamp"]),
            f'{incident["risk_score"]:.0f}',
            str(incident["severity"]),
            status,
        )

    console.print(table)

    suspicious_count = sum(
        1
        for incident in incidents
        if incident.get("is_suspicious")
    )

    console.print(
        f"\nTotal incidents: "
        f"{len(incidents)}"
    )

    console.print(
        f"Suspicious incidents: "
        f"{suspicious_count}"
    )