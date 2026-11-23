"""CLI orchestration for the common local/imported behavioral workflow."""

import json
import sqlite3
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from threatlens.collectors.device import collect_device_observation
from threatlens.config import database_path
from threatlens.detection.device import DeviceDetectionService
from threatlens.ingestion.device import load_document
from threatlens.schema.device import DeviceObservation, parse_document
from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.files import write_private_text
from threatlens.storage.repositories import IncidentRepository

console = Console()


def _service() -> DeviceDetectionService:
    return DeviceDetectionService(IncidentRepository(ThreatLensDatabase(database_path())))


def _local(device_id: str | None, sources: str | None) -> DeviceObservation:
    observation = collect_device_observation(device_id)
    if sources is not None:
        names = set(sources.split(","))
        if not names or names - {"system", "network", "process"}:
            raise ValueError("--sources must be a comma-separated subset of system,network,process")
        observation = DeviceObservation(
            observation.device_id,
            observation.device_type,
            observation.timestamp,
            observation.window_seconds,
            {k: v for k, v in observation.sources.items() if k in names},
            {k: v for k, v in observation.unavailable.items() if k in names},
        )
    # Run local data through exactly the same validation as imported data.
    return parse_document(_document([observation]))[0]


def _document(observations: list[DeviceObservation]) -> dict:
    first = observations[0]
    return {
        "schema_version": 1,
        "device_id": first.device_id,
        "device_type": first.device_type,
        "observations": [
            {k: v for k, v in row.to_dict().items() if k not in {"device_id", "device_type"}}
            for row in observations
        ],
    }


def _error(error: Exception) -> None:
    typer.echo(f"ThreatLens: {error}", err=True)
    raise typer.Exit(2)


def scan(
    input_path: Path | None = typer.Option(
        None, "--input", help="Versioned device telemetry JSON."
    ),
    device_id: str | None = typer.Option(
        None, "--device-id", help="Stable identity for local collection."
    ),
    sources: str | None = typer.Option(
        None, "--sources", help="Local source profile, e.g. system,process."
    ),
    json_output: bool = typer.Option(False, "--json"),
    fail_on_alert: bool = typer.Option(
        False, "--fail-on-alert", help="Exit 3 when a suspicious window is detected."
    ),
) -> None:
    """Assess local or imported telemetry against an explicitly learned baseline."""
    try:
        if input_path and (device_id or sources):
            raise ValueError("--device-id and --sources apply only to local collection")
        observations = load_document(input_path) if input_path else [_local(device_id, sources)]
        results = _service().scan(observations)
    except (OSError, ValueError, TypeError, sqlite3.Error) as error:
        _error(error)
    if json_output:
        typer.echo(json.dumps({"results": results}, indent=2, allow_nan=False))
    else:
        for result in results:
            coverage = result.get("coverage", {})
            text = f"Device: {result['device_type']} / {result['device_id']}\nStatus: {result['status']}\nBaseline: {result['baseline_size']} observations"
            if "risk" in result:
                text += (
                    f"\nRisk: {result['risk']['risk_score']:.0f}/100 ({result['risk']['severity']})"
                )
                text += f"\nCoverage: {'DEGRADED' if coverage['degraded'] else 'complete for trained profile'}"
                text += f"\n{result['explanation']['summary']}"
                for evidence in result["explanation"]["evidence"]:
                    text += f"\n• {evidence['description']}"
            else:
                text += "\nRun 'threatlens learn' on trusted normal telemetry first."
            if "incident_id" in result:
                action = "created" if result.get("incident_created", True) else "continuing"
                text += f"\nIncident {action}: #{result['incident_id']}"
            console.print(Panel(Text(text), title="ThreatLens Scan"))
    if any(row["status"] == "INSUFFICIENT_BASELINE" for row in results):
        raise typer.Exit(4)
    if fail_on_alert and any(row["is_suspicious"] for row in results):
        raise typer.Exit(3)


def learn(
    input_path: Path | None = typer.Option(None, "--input"),
    samples: int = typer.Option(30, "--samples", min=1, max=500),
    interval: float = typer.Option(
        1.0, "--interval", min=0.0, max=3600.0, help="Pause between local one-second samples."
    ),
    device_id: str | None = typer.Option(None, "--device-id"),
    sources: str | None = typer.Option(None, "--sources"),
    replace: bool = typer.Option(
        False, "--replace", help="Replace this device's trusted baseline and previous state."
    ),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Explicitly trust known-normal telemetry. Scans never update the baseline."""
    try:
        if input_path and (device_id or sources):
            raise ValueError("--device-id and --sources apply only to local collection")
        if input_path:
            observations = load_document(input_path)
        else:
            observations = []
            for number in range(samples):
                if number:
                    time.sleep(interval)
                observations.append(_local(device_id, sources))
        result = _service().learn(observations, replace=replace)
    except (OSError, ValueError, TypeError, sqlite3.Error) as error:
        _error(error)
    typer.echo(
        json.dumps(result, indent=2)
        if json_output
        else f"{result['device']}: {result['baseline_size']}/{result['required']} trusted windows; ready={result['ready']}. Baseline frozen."
    )


def collect(
    output: Path = typer.Option(..., "--output", "-o"),
    samples: int = typer.Option(1, "--samples", min=1, max=500),
    interval: float = typer.Option(1.0, "--interval", min=0.0, max=3600.0),
    device_id: str | None = typer.Option(None, "--device-id"),
    sources: str | None = typer.Option(None, "--sources"),
) -> None:
    """Export aggregate local telemetry for inspection, learning, or offline scanning."""
    try:
        observations = []
        for number in range(samples):
            if number:
                time.sleep(interval)
            observations.append(_local(device_id, sources))
        write_private_text(output, json.dumps(_document(observations), indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError) as error:
        _error(error)
    typer.echo(f"Telemetry written to {output}")
