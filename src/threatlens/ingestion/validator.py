from datetime import datetime
from math import isfinite
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
        raise ValueError(f"Missing telemetry fields: {sorted(missing)}")

    for field in REQUIRED_FIELDS - {"timestamp"}:
        value = data[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{field} must be a finite number")
    try:
        stamp = datetime.fromisoformat(data["timestamp"])
        if stamp.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
    except (TypeError, ValueError) as error:
        raise ValueError("timestamp must be an ISO-8601 datetime with timezone") from error
    for field in ("process_count", "uptime_seconds"):
        if not float(data[field]).is_integer():
            raise ValueError(f"{field} must be an integer")

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
