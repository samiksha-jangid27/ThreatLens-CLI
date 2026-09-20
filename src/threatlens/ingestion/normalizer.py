from typing import Any

from threatlens.schema.telemetry import SystemTelemetry


def normalize_system_telemetry(
    telemetry: SystemTelemetry,
) -> dict[str, Any]:
    """Convert system telemetry into a stable ML-ready dictionary."""

    data = telemetry.to_dict()

    return {
        "timestamp": data["timestamp"],
        "cpu_percent": float(data["cpu_percent"]),
        "memory_percent": float(data["memory_percent"]),
        "memory_available_mb": float(data["memory_available_mb"]),
        "load_average_1m": float(data["load_average_1m"]),
        "process_count": int(data["process_count"]),
        "uptime_seconds": int(data["uptime_seconds"]),
        "disk_percent": float(data["disk_percent"]),
    }