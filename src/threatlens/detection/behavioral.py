from statistics import median
from typing import Any


class BehavioralDeviationDetector:
    """
    Detect behavioral deviations using a robust baseline.

    The detector uses the median and Median Absolute Deviation
    (MAD) instead of relying only on mean/std. This makes the
    baseline less sensitive to extreme historical observations.

    For near-zero variance features, the detector also requires
    a meaningful absolute deviation before flagging an anomaly.
    """

    def __init__(
        self,
        threshold: float = 3.0,
        minimum_std: float = 1e-6,
        minimum_relative_deviation: float = 0.10,
        minimum_absolute_deviation: float = 1.0,
    ) -> None:
        if threshold <= 0:
            raise ValueError(
                "threshold must be greater than zero."
            )

        if minimum_std <= 0:
            raise ValueError(
                "minimum_std must be greater than zero."
            )

        if minimum_relative_deviation < 0:
            raise ValueError(
                "minimum_relative_deviation must not be negative."
            )

        if minimum_absolute_deviation < 0:
            raise ValueError(
                "minimum_absolute_deviation must not be negative."
            )

        self.threshold = threshold
        self.minimum_std = minimum_std
        self.minimum_relative_deviation = (
            minimum_relative_deviation
        )
        self.minimum_absolute_deviation = (
            minimum_absolute_deviation
        )

    def analyze(
        self,
        current: dict[str, float],
        baseline: list[dict[str, float]],
    ) -> dict[str, Any]:
        """
        Compare the current observation against a robust baseline.
        """

        if not baseline:
            raise ValueError(
                "At least one baseline observation is required."
            )

        signals: dict[
            str,
            dict[str, float | bool],
        ] = {}

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

            baseline_median = float(
                median(values)
            )

            absolute_deviations = [
                abs(value - baseline_median)
                for value in values
            ]

            mad = float(
                median(
                    absolute_deviations
                )
            )

            raw_deviation = (
                float(current_value)
                - baseline_median
            )

            absolute_deviation = abs(
                raw_deviation
            )

            meaningful_deviation = max(
                self.minimum_absolute_deviation,
                abs(baseline_median)
                * self.minimum_relative_deviation,
                self.minimum_std,
            )

            # -------------------------------------------------
            # ROBUST Z-SCORE
            # -------------------------------------------------

            if mad > self.minimum_std:
                z_score = (
                    0.6745
                    * raw_deviation
                    / mad
                )

                is_anomalous = (
                    abs(z_score)
                    >= self.threshold
                )

            # -------------------------------------------------
            # LOW-VARIANCE BASELINE
            # -------------------------------------------------

            else:
                # When historical variance is almost zero,
                # do not treat every tiny change as anomalous.
                z_score = (
                    raw_deviation
                    / meaningful_deviation
                )

                is_anomalous = (
                    absolute_deviation
                    >= (
                        meaningful_deviation
                        * self.threshold
                    )
                )

            signals[feature_name] = {
                "is_anomalous": is_anomalous,
                "current": float(current_value),
                "baseline_mean": (
                    sum(values) / len(values)
                ),
                "baseline_median": baseline_median,
                "baseline_std": (
                    self._standard_deviation(
                        values
                    )
                ),
                "mad": mad,
                "minimum_meaningful_deviation": (
                    meaningful_deviation
                ),
                "z_score": z_score,
            }

        anomalous_features = [
            feature_name
            for feature_name, result in signals.items()
            if bool(
                result["is_anomalous"]
            )
        ]

        return {
            "is_anomaly": bool(
                anomalous_features
            ),
            "anomalous_features": (
                anomalous_features
            ),
            "signal_count": len(
                anomalous_features
            ),
            "signals": signals,
        }

    @staticmethod
    def _standard_deviation(
        values: list[float],
    ) -> float:
        """
        Calculate population standard deviation.
        """

        if not values:
            return 0.0

        mean = sum(values) / len(values)

        variance = sum(
            (value - mean) ** 2
            for value in values
        ) / len(values)

        return variance ** 0.5