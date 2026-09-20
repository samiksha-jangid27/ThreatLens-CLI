from typing import Any


class BehavioralDeviationDetector:
    """
    Detect behavioral deviations using baseline statistics.

    The detector learns the mean and standard deviation of
    previously observed normal behavior and measures how far
    the current observation deviates from that baseline.
    """

    def __init__(
        self,
        threshold: float = 3.0,
        minimum_std: float = 1e-6,
    ) -> None:
        if threshold <= 0:
            raise ValueError(
                "threshold must be greater than zero."
            )

        if minimum_std <= 0:
            raise ValueError(
                "minimum_std must be greater than zero."
            )

        self.threshold = threshold
        self.minimum_std = minimum_std

    def analyze(
        self,
        current: dict[str, float],
        baseline: list[dict[str, float]],
    ) -> dict[str, Any]:
        """
        Compare the current observation against a normal baseline.
        """

        if not baseline:
            raise ValueError(
                "At least one baseline observation is required."
            )

        signals: dict[str, dict[str, float | bool]] = {}

        for feature_name, current_value in current.items():
            values = [
                float(
                    observation.get(
                        feature_name,
                        0.0,
                    )
                )
                for observation in baseline
            ]

            mean = sum(values) / len(values)

            variance = sum(
                (value - mean) ** 2
                for value in values
            ) / len(values)

            standard_deviation = max(
                variance ** 0.5,
                self.minimum_std,
            )

            z_score = (
                float(current_value) - mean
            ) / standard_deviation

            is_anomalous = (
                abs(z_score) >= self.threshold
            )

            signals[feature_name] = {
                "is_anomalous": is_anomalous,
                "current": float(current_value),
                "baseline_mean": mean,
                "baseline_std": standard_deviation,
                "z_score": z_score,
            }

        anomalous_features = [
            feature_name
            for feature_name, result in signals.items()
            if bool(result["is_anomalous"])
        ]

        return {
            "is_anomaly": bool(anomalous_features),
            "anomalous_features": anomalous_features,
            "signal_count": len(anomalous_features),
            "signals": signals,
        }
