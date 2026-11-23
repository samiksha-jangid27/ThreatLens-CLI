import json
import sqlite3

import typer

from threatlens.config import database_path
from threatlens.detection.device import DeviceDetectionService
from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.repositories import IncidentRepository


def status(json_output: bool = typer.Option(False, "--json")) -> None:
    """Show actual per-device baseline readiness and state location."""
    try:
        path = database_path()
        devices = DeviceDetectionService(IncidentRepository(ThreatLensDatabase(path))).status()
    except (OSError, sqlite3.Error, ValueError) as error:
        typer.echo(f"ThreatLens: {error}", err=True)
        raise typer.Exit(2) from None
    result = {
        "database": str(path),
        "devices": devices,
        "baseline_policy": "frozen; explicit learning only",
    }
    if json_output:
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(f"State: {path}")
        if not devices:
            typer.echo("No baselines learned. Run 'threatlens learn --help'.")
        for device in devices:
            typer.echo(
                f"{device['device']}: {device['baseline_size']}/30 windows; ready={device['ready']}"
            )
