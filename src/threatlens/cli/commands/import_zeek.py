import json
from pathlib import Path

import typer

from threatlens.ingestion.zeek import convert_zeek
from threatlens.storage.files import write_private_text


def import_zeek(
    input_path: Path = typer.Option(..., "--input"),
    output: Path = typer.Option(..., "--output"),
    device_id: str = typer.Option(
        ..., "--device-id", help="Identity of the Zeek sensor or monitored network."
    ),
    window_seconds: int = typer.Option(60, "--window-seconds", min=1, max=86400),
) -> None:
    """Convert a Zeek conn.log TSV export into validated network telemetry."""
    try:
        document = convert_zeek(input_path, device_id, window_seconds)
        write_private_text(output, json.dumps(document, indent=2, allow_nan=False))
    except (OSError, ValueError, UnicodeError) as error:
        typer.echo(f"ThreatLens: {error}", err=True)
        raise typer.Exit(2) from None
    typer.echo(f"Converted {len(document['observations'])} occupied windows to {output}")
