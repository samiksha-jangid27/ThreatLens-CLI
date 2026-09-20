import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from threatlens.explainability.explainer import (
    ThreatExplainer,
)
from threatlens.collectors.network import (
    collect_network_telemetry,
)
from threatlens.collectors.processes import (
    collect_process_telemetry,
)
from threatlens.collectors.system import (
    collect_system_telemetry,
)
from threatlens.detection.pipeline import (
    ThreatScanPipeline,
)
from threatlens.features.system import (
    extract_system_features,
)
from threatlens.models.isolation_forest import (
    IsolationForestDetector,
)
from threatlens.schema.telemetry import (
    SystemTelemetry,
)
from threatlens.storage.database import (
    ThreatLensDatabase,
)
from threatlens.storage.repositories import (
    IncidentRepository,
)

console = Console()

BASELINE_PATH = (
    Path.home()
    / ".threatlens"
    / "system_baseline.json"
)

NETWORK_BASELINE_PATH = (
    Path.home()
    / ".threatlens"
    / "network_baseline.json"
)

PROCESS_BASELINE_PATH = (
    Path.home()
    / ".threatlens"
    / "process_baseline.json"
)

DATABASE_PATH = (
    Path.home()
    / ".threatlens"
    / "threatlens.db"
)


def _load_baseline() -> list[dict[str, float]]:
    """Load the stored system behavioral baseline."""

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
    """Persist the system behavioral baseline."""

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


def _load_json_baseline(
    path: Path,
) -> list[dict]:
    """Load a JSON behavioral baseline."""

    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def _save_json_baseline(
    path: Path,
    observations: list[dict],
) -> None:
    """Persist a JSON behavioral baseline."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
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

def _format_explanation(
    explanation: dict,
) -> str:
    """Format detection evidence for terminal output."""

    lines = []

    if not explanation["evidence"]:
        return "No anomalous behavioral evidence identified."

    for evidence in explanation["evidence"]:
        lines.append(
            f"• {evidence['description']}"
        )

        details = evidence.get(
            "details",
            {},
        )

        anomalous_features = details.get(
            "anomalous_features"
        )

        if anomalous_features:
            lines.append(
                "  Features: "
                + ", ".join(
                    anomalous_features
                )
            )

    lines.append("")
    lines.append(
        f"Summary: {explanation['summary']}"
    )

    return "\n".join(lines)


def scan() -> None:
    """Run a multi-signal behavioral system scan."""

    current = collect_system_telemetry()
    current_network = collect_network_telemetry()
    current_processes = collect_process_telemetry()

    baseline = _load_baseline()

    network_baseline = _load_json_baseline(
        NETWORK_BASELINE_PATH
    )

    process_baseline = _load_json_baseline(
        PROCESS_BASELINE_PATH
    )

    # ---------------------------------------------------------
    # BASELINE COLLECTION
    # ---------------------------------------------------------

    if (
        len(baseline) < 5
        or len(network_baseline) < 5
        or len(process_baseline) < 5
    ):
        current_features = extract_system_features(
            current.to_dict()
        )

        baseline.append(current_features)

        network_baseline.append(
            current_network.to_dict()
        )

        process_baseline.append(
            current_processes
        )

        # Keep only the latest 100 observations.
        baseline = baseline[-100:]
        network_baseline = network_baseline[-100:]
        process_baseline = process_baseline[-100:]

        _save_baseline(baseline)

        _save_json_baseline(
            NETWORK_BASELINE_PATH,
            network_baseline,
        )

        _save_json_baseline(
            PROCESS_BASELINE_PATH,
            process_baseline,
        )

        console.print(
            Panel(
                f"System observations: "
                f"{min(len(baseline), 5)}/5\n"
                f"Network observations: "
                f"{min(len(network_baseline), 5)}/5\n"
                f"Process observations: "
                f"{min(len(process_baseline), 5)}/5\n\n"
                "ThreatLens needs at least 5 normal "
                "observations for each telemetry source "
                "before running anomaly detection.",
                title="ThreatLens Baseline",
            )
        )

        return

    # ---------------------------------------------------------
    # TRAIN BEHAVIORAL MODEL
    # ---------------------------------------------------------

    detector = IsolationForestDetector(
        contamination=0.2,
        random_state=42,
    )

    detector.fit(baseline)

    # ---------------------------------------------------------
    # RECONSTRUCT PREVIOUS SYSTEM TELEMETRY
    # ---------------------------------------------------------

    previous_features = baseline[-1]

    previous = SystemTelemetry(
        timestamp=current.timestamp,
        cpu_percent=previous_features["cpu_percent"],
        memory_percent=previous_features[
            "memory_percent"
        ],
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

    # ---------------------------------------------------------
    # PREVIOUS NETWORK + PROCESS OBSERVATIONS
    # ---------------------------------------------------------

    previous_network = network_baseline[-1]

    previous_processes = process_baseline[-1]

    # ---------------------------------------------------------
    # RUN MULTI-SIGNAL DETECTION PIPELINE
    # ---------------------------------------------------------

    pipeline = ThreatScanPipeline(
        isolation_forest=detector,
    )
    explainer = ThreatExplainer()

    result = pipeline.scan(
    current=current,
    previous=previous,
    baseline=baseline,
    network_baseline=network_baseline,
    process_baseline=process_baseline,
    current_network=current_network,
    previous_network=previous_network,
    current_processes=current_processes,
    previous_processes=previous_processes,
    )
    explanation = explainer.explain(result)
    # ---------------------------------------------------------
    # SUSPICIOUS RESULT
    # ---------------------------------------------------------

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
                f"[bold]Signals:[/bold] "
                f"{', '.join(result['risk']['triggered_signals'])}\n"
                f"[bold red]Incident created:[/bold red] "
                f"#{incident_id}",
                title="ThreatLens Scan",
            )
        )

        console.print()
        console.print(
            Panel(
                _format_explanation(explanation),
                title="ThreatLens Evidence",
            )
        )

    # ---------------------------------------------------------
    # NORMAL RESULT
    # ---------------------------------------------------------

    else:
        console.print(
            Panel(
                "[bold green]Status:[/bold green] "
                "NORMAL\n"
                f"[bold]Anomaly Score:[/bold] "
                f"{result['model']['anomaly_score']:.4f}\n"
                f"[bold]Temporal Signals:[/bold] "
                f"{result['temporal']['signal_count']}\n"
                f"[bold]Network Signal:[/bold] "
                f"{result['signals'].get('network_anomaly', False)}\n"
                f"[bold]Process Signal:[/bold] "
                f"{result['signals'].get('process_anomaly', False)}\n\n"
                "No correlated behavioral anomaly detected.",
                title="ThreatLens Scan",
            )
        )

    # ---------------------------------------------------------
    # LEARN ONLY FROM NORMAL BEHAVIOR
    # ---------------------------------------------------------

    if not result["is_suspicious"]:
        current_features = extract_system_features(
            current.to_dict()
        )

        baseline.append(
            current_features
        )

        network_baseline.append(
            current_network.to_dict()
        )

        process_baseline.append(
            current_processes
        )

        # Keep baselines bounded.
        baseline = baseline[-100:]
        network_baseline = network_baseline[-100:]
        process_baseline = process_baseline[-100:]

        _save_baseline(
            baseline
        )

        _save_json_baseline(
            NETWORK_BASELINE_PATH,
            network_baseline,
        )

        _save_json_baseline(
            PROCESS_BASELINE_PATH,
            process_baseline,
        )