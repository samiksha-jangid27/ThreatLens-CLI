import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from threatlens.collectors.system import collect_system_telemetry
from threatlens.detection.pipeline import ThreatScanPipeline
from threatlens.features.system import extract_system_features
from threatlens.models.isolation_forest import IsolationForestDetector
from threatlens.schema.telemetry import SystemTelemetry
from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.repositories import IncidentRepository


console = Console()

BASELINE_PATH = (
    Path.home()
    / ".threatlens"
    / "system_baseline.json"
)

DATABASE_PATH = (
    Path.home()
    / ".threatlens"
    / "threatlens.db"
)


def _load_baseline() -> list[dict[str, float]]:
    """Load the stored behavioral baseline."""

    if not BASELINE_PATH.exists():
        return []

    with BASELINE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def _save_baseline(
    observations: list[dict[str, float]],
) -> None:
    """Persist the behavioral baseline."""

    BASELINE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with BASELINE_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            observations,
            file,
            indent=2,
        )


def _get_repository() -> IncidentRepository:
    """Create the default incident repository."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return IncidentRepository(
        ThreatLensDatabase(DATABASE_PATH)
    )


def scan() -> None:
    """Run a behavioral system scan."""

    current = collect_system_telemetry()
    baseline = _load_baseline()

    if len(baseline) < 5:
        current_features = extract_system_features(
            current.to_dict()
        )

        baseline.append(current_features)
        _save_baseline(baseline)

        console.print(
            Panel(
                f"Collected baseline observation "
                f"{len(baseline)}/5.\n\n"
                "ThreatLens needs at least 5 normal "
                "observations before running anomaly detection.",
                title="ThreatLens Baseline",
            )
        )
        return

    detector = IsolationForestDetector(
        contamination=0.2,
        random_state=42,
    )

    detector.fit(baseline)

    previous_features = baseline[-1]

    previous = SystemTelemetry(
        timestamp=current.timestamp,
        cpu_percent=previous_features["cpu_percent"],
        memory_percent=previous_features["memory_percent"],
        memory_available_mb=previous_features[
            "memory_available_mb"
        ],
        load_average_1m=previous_features[
            "load_average_1m"
        ],
        process_count=int(
            previous_features["process_count"]
        ),
        uptime_seconds=int(
            previous_features["uptime_seconds"]
        ),
        disk_percent=previous_features[
            "disk_percent"
        ],
    )

    pipeline = ThreatScanPipeline(
        isolation_forest=detector,
    )

    result = pipeline.scan(
        current=current,
        previous=previous,
    )

    if result["is_suspicious"]:
        repository = _get_repository()

        incident = {
            "timestamp": current.timestamp.isoformat(),
            "signals": result["signals"],
            "correlation": result["correlation"],
            "risk": result["risk"],
            "is_suspicious": result["is_suspicious"],
        }

        incident_id = repository.create(
            incident
        )

        console.print(
            Panel(
                "[bold red]Status:[/bold red] "
                "SUSPICIOUS\n"
                f"[bold]Risk Score:[/bold] "
                f"{result['risk']['risk_score']:.0f}/100\n"
                f"[bold]Severity:[/bold] "
                f"{result['risk']['severity']}\n"
                f"[bold red]Incident created:[/bold red] "
                f"#{incident_id}",
                title="ThreatLens Scan",
            )
        )
    else:
        console.print(
            Panel(
                "[bold green]Status:[/bold green] NORMAL\n"
                f"[bold]Anomaly Score:[/bold] "
                f"{result['model']['anomaly_score']:.4f}\n"
                f"[bold]Temporal Signals:[/bold] "
                f"{result['temporal']['signal_count']}\n\n"
                "No correlated behavioral anomaly detected.",
                title="ThreatLens Scan",
            )
        )

    # Only learn from observations that were
    # not considered suspicious.
    if not result["is_suspicious"]:
        current_features = extract_system_features(
            current.to_dict()
        )

        baseline.append(current_features)

        # Keep the baseline bounded.
        baseline = baseline[-100:]

        _save_baseline(baseline)