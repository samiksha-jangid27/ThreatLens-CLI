from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestDetector:
    """Detect anomalous behavioral observations."""

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> None:
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )

        self.feature_names: list[str] = []
        self.is_fitted = False

    def fit(
        self,
        observations: list[dict[str, float]],
    ) -> None:
        """Train the detector on historical behavioral observations."""

        if not observations:
            raise ValueError("At least one observation is required.")

        self.feature_names = sorted(set(observations[0]) - {"uptime_seconds"})
        if not self.feature_names:
            raise ValueError("At least one behavioral feature is required.")
        expected = set(self.feature_names)
        for observation in observations:
            if set(observation) - {"uptime_seconds"} != expected:
                raise ValueError("Baseline observations must have identical feature names.")
            if any(
                isinstance(observation[name], bool) or not np.isfinite(observation[name])
                for name in self.feature_names
            ):
                raise ValueError("Features must be finite numbers.")

        matrix = np.array(
            [
                [float(observation[name]) for name in self.feature_names]
                for observation in observations
            ]
        )

        self.model.fit(matrix)
        self.is_fitted = True

    def predict(
        self,
        observation: dict[str, float],
    ) -> dict[str, Any]:
        """Predict whether an observation is anomalous."""

        if not self.is_fitted:
            raise RuntimeError("Detector must be fitted before prediction.")

        if set(observation) - {"uptime_seconds"} != set(self.feature_names):
            raise ValueError("Observation feature names do not match the model baseline.")
        if any(
            isinstance(observation[name], bool) or not np.isfinite(observation[name])
            for name in self.feature_names
        ):
            raise ValueError("Features must be finite numbers.")

        values = np.array([[float(observation[name]) for name in self.feature_names]])

        prediction = self.model.predict(values)[0]
        score = self.model.decision_function(values)[0]

        return {
            "is_anomaly": bool(prediction == -1),
            "prediction": int(prediction),
            "anomaly_score": float(score),
        }
