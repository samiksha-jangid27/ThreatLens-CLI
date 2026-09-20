from typing import Any


REQUIRED_FIELDS = {
    "timestamp",
    "cpu_percent",
    "memory_percent",
    "memory_available_mb",
    "load_average_1m",
    "process_count",
    "uptime_seconds",
    "disk_percent",
}


def validate_system_telemetry(data: dict[str, Any]) -> None:
    """Validate normalized system telemetry."""

    missing = REQUIRED_FIELDS - data.keys()

    if missing:
        raise ValueError(
            f"Missing telemetry fields: {sorted(missing)}"
        )

    if not 0 <= data["cpu_percent"] <= 100:
        raise ValueError("cpu_percent must be between 0 and 100")

    if not 0 <= data["memory_percent"] <= 100:
        raise ValueError("memory_percent must be between 0 and 100")

    if data["memory_available_mb"] < 0:
        raise ValueError("memory_available_mb cannot be negative")

    if data["load_average_1m"] < 0:
        raise ValueError("load_average_1m cannot be negative")

    if data["process_count"] < 0:
        raise ValueError("process_count cannot be negative")

    if data["uptime_seconds"] < 0:
        raise ValueError("uptime_seconds cannot be negative")

    if not 0 <= data["disk_percent"] <= 100:
        raise ValueError("disk_percent must be between 0 and 100")