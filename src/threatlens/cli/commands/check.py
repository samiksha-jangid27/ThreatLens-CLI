"""Inspect this computer's real telemetry without training or changing detection state."""

import json
import platform
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from threatlens.cli.errors import handle_errors
from threatlens.collectors.device import collect_device_observation
from threatlens.storage.files import write_private_text


@handle_errors
def check(
    json_output: bool = typer.Option(False, "--json", help="Print the live snapshot as JSON."),
    output: Path | None = typer.Option(None, "--output", help="Save a private JSON snapshot."),
) -> None:
    """Inspect this machine's current metrics and collection visibility; no baseline required."""
    observation = collect_device_observation()
    result = {
        "data_origin": "live_local_telemetry",
        "platform": platform.system(),
        **observation.to_dict(),
        "coverage": {
            "available_sources": sorted(observation.sources),
            "unavailable_sources": observation.unavailable,
            "degraded": bool(observation.unavailable),
        },
        "security_assessment": "NOT_PERFORMED",
        "note": "A live snapshot does not establish whether this machine is compromised. Explicit trusted learning is required before behavioral scans.",
    }
    if output is not None:
        write_private_text(output, json.dumps(result, indent=2, allow_nan=False))
    if json_output:
        typer.echo(json.dumps(result, indent=2, allow_nan=False))
        return
    console = Console(markup=False)
    console.print(f"Live local check: {observation.device_id} ({result['platform']})")
    console.print(f"Observed: {observation.timestamp}")
    table = Table(title="Actual current device metrics")
    table.add_column("Source")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for source, features in observation.sources.items():
        for name, value in features.items():
            table.add_row(source, name, f"{value:.2f}")
    console.print(table)
    for source, reason in observation.unavailable.items():
        console.print(f"UNAVAILABLE: {source}: {reason}")
    console.print(result["note"])
    console.print(
        "Next: approve normal telemetry with 'learn --sources system --samples 30', then 'scan --sources system'."
    )
    if output is not None:
        console.print(f"Snapshot saved to {output}")
