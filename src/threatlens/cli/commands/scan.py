import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from threatlens.collectors.system import collect_system_telemetry
from threatlens.features.system import extract_system_features
from threatlens.models.isolation_forest import IsolationForestDetector


console = Console()

BASELINE_PATH = (
    Path.home()
    / ".threatlens"
    / "system_baseline.json"
)


def _load_baseline() -> list[dict[str, float]]:
    """Load the stored behavioral baseline."""

    if not BASELINE_PATH.exists():
        return []

    with BASELINE_PATH.open("r", encoding="utf-8") as file:
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


def scan() -> None:
    """Run a behavioral system scan."""

    telemetry = collect_system_telemetry()

    current_features = extract_system_features(
        telemetry.to_dict()
    )

    baseline = _load_baseline()

    if len(baseline) < 5:
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
        contamination=0.1,
        random_state=42,
    )

    detector.fit(baseline)

    result = detector.predict(
        current_features
    )

    if result["is_anomaly"]:
        severity = "SUSPICIOUS"
        message = (
            "Behavior differs significantly "
            "from the learned baseline."
        )
    else:
        severity = "NORMAL"
        message = (
            "No significant behavioral anomaly detected."
        )

    console.print(
        Panel(
            f"[bold]Status:[/bold] {severity}\n"
            f"[bold]Anomaly Score:[/bold] "
            f"{result['anomaly_score']:.4f}\n\n"
            f"{message}",
            title="ThreatLens Scan",
        )
    )
