from typing import Any


def calculate_change(
    current: float,
    previous: float,
) -> float:
    """Calculate the change between two observations."""

    return current - previous


def extract_temporal_features(
    current: dict[str, Any],
    previous: dict[str, Any],
) -> dict[str, float]:
    """Extract behavioral changes between consecutive observations."""

    return {
        "cpu_delta": calculate_change(
            float(current["cpu_percent"]),
            float(previous["cpu_percent"]),
        ),
        "memory_delta": calculate_change(
            float(current["memory_percent"]),
            float(previous["memory_percent"]),
        ),
        "load_delta": calculate_change(
            float(current["load_average_1m"]),
            float(previous["load_average_1m"]),
        ),
        "process_delta": calculate_change(
            float(current["process_count"]),
            float(previous["process_count"]),
        ),
        "disk_delta": calculate_change(
            float(current["disk_percent"]),
            float(previous["disk_percent"]),
        ),
    }