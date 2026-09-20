from typing import Any

from threatlens.detection.correlation import EventCorrelator
from threatlens.detection.risk import RiskScorer


class DetectionEngine:
    """Combine behavioral detection signals into one result."""

    def __init__(
        self,
        correlator: EventCorrelator | None = None,
        risk_scorer: RiskScorer | None = None,
    ) -> None:
        self.correlator = correlator or EventCorrelator()
        self.risk_scorer = risk_scorer or RiskScorer()

    def analyze(
        self,
        signals: dict[str, bool],
    ) -> dict[str, Any]:
        """Run correlation and risk scoring on detection signals."""

        correlation = self.correlator.correlate(signals)
        risk = self.risk_scorer.score(signals)

        return {
            "signals": dict(signals),
            "correlation": correlation,
            "risk": risk,
            "is_suspicious": correlation["is_correlated"],
        }
