from typing import Any


class EventCorrelator:
    """Combine multiple detection signals into a correlated security event."""

    def __init__(self, minimum_signals: int = 2) -> None:
        if minimum_signals < 1:
            raise ValueError("minimum_signals must be at least 1.")

        self.minimum_signals = minimum_signals

    def correlate(
        self,
        signals: dict[str, bool],
    ) -> dict[str, Any]:
        """Correlate independent detection signals."""

        triggered = [
            name
            for name, triggered in signals.items()
            if bool(triggered)
        ]

        signal_count = len(triggered)

        return {
            "is_correlated": signal_count >= self.minimum_signals,
            "signal_count": signal_count,
            "triggered_signals": triggered,
        }
