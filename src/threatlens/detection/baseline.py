from typing import Any


class BehavioralBaseline:
    """Store normal behavioral statistics for a system."""

    def __init__(self) -> None:
        self.count = 0
        self.means: dict[str, float] = {}
        self.minimums: dict[str, float] = {}
        self.maximums: dict[str, float] = {}

    def update(self, features: dict[str, float]) -> None:
        """Update the baseline with a new observation."""

        self.count += 1

        for name, value in features.items():
            value = float(value)

            if name not in self.means:
                self.means[name] = value
                self.minimums[name] = value
                self.maximums[name] = value
                continue

            previous_count = self.count - 1

            self.means[name] = (
                self.means[name] * previous_count + value
            ) / self.count

            self.minimums[name] = min(
                self.minimums[name],
                value,
            )

            self.maximums[name] = max(
                self.maximums[name],
                value,
            )

    def summary(self) -> dict[str, Any]:
        """Return the learned behavioral baseline."""

        return {
            "observations": self.count,
            "means": dict(self.means),
            "minimums": dict(self.minimums),
            "maximums": dict(self.maximums),
        }