from pathlib import Path

import typer
from rich.console import Console

from threatlens.reporting.html import (
    generate_html_report,
)
from threatlens.reporting.json import (
    generate_json_report,
)
from threatlens.reporting.terminal import (
    print_terminal_report,
)
from threatlens.storage.database import (
    ThreatLensDatabase,
)
from threatlens.storage.repositories import (
    IncidentRepository,
)


console = Console()


def _get_repository() -> IncidentRepository:
    """Create the default ThreatLens repository."""

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


def report(
    format: str = typer.Option(
        "terminal",
        "--format",
        "-f",
        help="Report format: terminal, json, or html.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write the report to a file.",
    ),
) -> None:
    """Generate a ThreatLens incident report."""

    if format not in {
        "terminal",
        "json",
        "html",
    }:
        raise typer.BadParameter(
            "Format must be terminal, json, or html."
        )

    repository = _get_repository()

    incidents = repository.list_all()

    if format == "terminal":
        print_terminal_report(
            incidents
        )
        return

    if format == "json":
        content = generate_json_report(
            incidents
        )

        default_name = (
            "threatlens-report.json"
        )

    else:
        content = generate_html_report(
            incidents
        )

        default_name = (
            "threatlens-report.html"
        )

    output_path = (
        output
        or Path.home() / default_name
    )

    output_path.write_text(
        content,
        encoding="utf-8",
    )

    console.print(
        f"[green]Report written to:[/green] "
        f"{output_path}"
    )