from typing import Any


class RiskScorer:
    """Calculate a compromise risk score from detection signals."""

    DEFAULT_WEIGHTS = {
        "isolation_forest": 40,
        "temporal_anomaly": 25,
        "network_anomaly": 20,
        "process_anomaly": 15,
    }

    def __init__(
        self,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)

    def score(
        self,
        signals: dict[str, bool],
    ) -> dict[str, Any]:
        """Calculate a 0-100 risk score from triggered signals."""

        contributions: dict[str, float] = {}

        for name, triggered in signals.items():
            if bool(triggered):
                weight = float(self.weights.get(name, 0))
                contributions[name] = weight

        raw_score = sum(contributions.values())
        risk_score = min(100.0, raw_score)

        return {
            "risk_score": risk_score,
            "severity": self._severity(risk_score),
            "contributions": contributions,
            "triggered_signals": list(contributions.keys()),
        }

    @staticmethod
    def _severity(score: float) -> str:
        """Convert a numeric risk score into a severity level."""

        if score >= 80:
            return "CRITICAL"

        if score >= 60:
            return "HIGH"

        if score >= 30:
            return "MEDIUM"

        return "LOW"
