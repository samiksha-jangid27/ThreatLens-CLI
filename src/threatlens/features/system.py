from typing import Any


def extract_system_features(
    telemetry: dict[str, Any],
) -> dict[str, float]:
    """Extract ML-ready behavioral features from normalized telemetry."""

    return {
        "cpu_percent": float(telemetry["cpu_percent"]),
        "memory_percent": float(telemetry["memory_percent"]),
        "memory_available_mb": float(
            telemetry["memory_available_mb"]
        ),
        "load_average_1m": float(
            telemetry["load_average_1m"]
        ),
        "process_count": float(
            telemetry["process_count"]
        ),
        "uptime_seconds": float(
            telemetry["uptime_seconds"]
        ),
        "disk_percent": float(
            telemetry["disk_percent"]
        ),
    }