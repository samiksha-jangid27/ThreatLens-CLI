from typing import Any


class TemporalAnomalyDetector:
    """Detect sudden behavioral changes between observations."""

    def __init__(
        self,
        thresholds: dict[str, float] | None = None,
    ) -> None:
        self.thresholds = thresholds or {
            "cpu_percent": 30.0,
            "memory_percent": 20.0,
            "load_average_1m": 2.0,
            "process_count": 50.0,
            "disk_percent": 10.0,
        }

    def analyze(
        self,
        current: dict[str, Any],
        previous: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze changes between consecutive observations."""

        changes: dict[str, float] = {}
        triggered: dict[str, float] = {}

        for field, threshold in self.thresholds.items():
            current_value = float(current[field])
            previous_value = float(previous[field])

            delta = current_value - previous_value

            changes[field] = delta

            if abs(delta) >= threshold:
                triggered[field] = delta

        return {
            "is_anomaly": bool(triggered),
            "changes": changes,
            "triggered_signals": triggered,
            "signal_count": len(triggered),
        }
