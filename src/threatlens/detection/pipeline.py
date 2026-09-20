from typing import Any

from threatlens.detection.behavioral import (
    BehavioralDeviationDetector,
)
from threatlens.detection.engine import DetectionEngine
from threatlens.detection.temporal import (
    TemporalAnomalyDetector,
)
from threatlens.features.network import (
    extract_network_features,
)
from threatlens.features.network_temporal import (
    extract_network_temporal_features,
)
from threatlens.features.process import (
    extract_process_features,
)
from threatlens.features.system import (
    extract_system_features,
)
from threatlens.ingestion.normalizer import (
    normalize_system_telemetry,
)
from threatlens.ingestion.validator import (
    validate_system_telemetry,
)
from threatlens.models.isolation_forest import (
    IsolationForestDetector,
)
from threatlens.schema.network import (
    NetworkTelemetry,
)
from threatlens.schema.telemetry import (
    SystemTelemetry,
)


class ThreatScanPipeline:
    """
    Multi-signal behavioral threat detection pipeline.
    """

    def __init__(
        self,
        isolation_forest: IsolationForestDetector,
        temporal_detector: TemporalAnomalyDetector | None = None,
        behavioral_detector: BehavioralDeviationDetector | None = None,
        detection_engine: DetectionEngine | None = None,
    ) -> None:
        self.isolation_forest = isolation_forest

        self.temporal_detector = (
            temporal_detector
            or TemporalAnomalyDetector()
        )

        self.behavioral_detector = (
            behavioral_detector
            or BehavioralDeviationDetector()
        )

        self.detection_engine = (
            detection_engine
            or DetectionEngine()
        )

    def scan(
        self,
        current: SystemTelemetry,
        previous: SystemTelemetry,
        baseline: list[dict[str, float]] | None = None,
        network_baseline: list[dict[str, Any]] | None = None,
        process_baseline: list[dict[str, Any]] | None = None,
        current_network: NetworkTelemetry | dict[str, Any] | None = None,
        previous_network: NetworkTelemetry | dict[str, Any] | None = None,
        current_processes: dict[str, Any] | None = None,
        previous_processes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run system, behavioral, temporal, network,
        and process anomaly detection.
        """

        current_normalized = (
            normalize_system_telemetry(current)
        )

        previous_normalized = (
            normalize_system_telemetry(previous)
        )

        validate_system_telemetry(
            current_normalized
        )

        validate_system_telemetry(
            previous_normalized
        )

        current_features = extract_system_features(
            current_normalized
        )

        previous_features = extract_system_features(
            previous_normalized
        )

        temporal_features = (
            self._system_temporal_features(
                current_features,
                previous_features,
            )
        )

        model_result = (
            self.isolation_forest.predict(
                current_features
            )
        )

        temporal_result = (
            self.temporal_detector.analyze(
                current_features,
                previous_features,
            )
        )

        signals: dict[str, bool] = {
            "isolation_forest": bool(
                model_result["is_anomaly"]
            ),
            "temporal_anomaly": bool(
                temporal_result["is_anomaly"]
            ),
        }

        behavioral_result = None

        if baseline:
            behavioral_result = (
                self.behavioral_detector.analyze(
                    current_features,
                    baseline,
                )
            )

            signals["behavioral_deviation"] = bool(
                behavioral_result["is_anomaly"]
            )

        # -------------------------------------------------
        # NETWORK ANALYSIS
        # -------------------------------------------------

        network_result = None

        if (
            current_network is not None
            and previous_network is not None
        ):
            current_network_features = (
                extract_network_features(
                    current_network
                )
            )

            previous_network_features = (
                extract_network_features(
                    previous_network
                )
            )

            network_temporal = (
                extract_network_temporal_features(
                    current_network_features,
                    previous_network_features,
                )
            )

            network_behavioral_result = None

            if network_baseline:
                network_feature_baseline = [
                    extract_network_features(
                        observation
                    )
                    for observation in network_baseline
                ]

                network_behavioral_result = (
                    self.behavioral_detector.analyze(
                        current_network_features,
                        network_feature_baseline,
                    )
                )

                network_anomaly = bool(
                    network_behavioral_result[
                        "is_anomaly"
                    ]
                )
            else:
                network_anomaly = any(
                    abs(value) >= 5.0
                    for value in network_temporal.values()
                )

            signals["network_anomaly"] = (
                network_anomaly
            )

            network_result = {
                "current_features": (
                    current_network_features
                ),
                "previous_features": (
                    previous_network_features
                ),
                "temporal_features": (
                    network_temporal
                ),
                "behavioral": (
                    network_behavioral_result
                ),
                "is_anomaly": network_anomaly,
            }

        # -------------------------------------------------
        # PROCESS ANALYSIS
        # -------------------------------------------------

        process_result = None

        if (
            current_processes is not None
            and previous_processes is not None
        ):
            current_process_features = (
                extract_process_features(
                    current_processes
                )
            )

            previous_process_features = (
                extract_process_features(
                    previous_processes
                )
            )

            process_deltas = {
                key: (
                    current_process_features[key]
                    - previous_process_features.get(
                        key,
                        0.0,
                    )
                )
                for key in current_process_features
            }

            process_behavioral_result = None

            if process_baseline:
                process_feature_baseline = [
                    extract_process_features(
                        observation
                    )
                    for observation in process_baseline
                ]

                process_behavioral_result = (
                    self.behavioral_detector.analyze(
                        current_process_features,
                        process_feature_baseline,
                    )
                )

                process_anomaly = bool(
                    process_behavioral_result[
                        "is_anomaly"
                    ]
                )
            else:
                process_anomaly = any(
                    abs(value) >= 10.0
                    for value in process_deltas.values()
                )

            signals["process_anomaly"] = (
                process_anomaly
            )

            process_result = {
                "current_features": (
                    current_process_features
                ),
                "previous_features": (
                    previous_process_features
                ),
                "deltas": process_deltas,
                "behavioral": (
                    process_behavioral_result
                ),
                "is_anomaly": process_anomaly,
            }

        # -------------------------------------------------
        # CORRELATION + RISK
        # -------------------------------------------------

        detection_result = (
            self.detection_engine.analyze(
                signals
            )
        )

        return {
            "current": current_normalized,
            "previous": previous_normalized,
            "features": current_features,
            "temporal_features": temporal_features,
            "model": model_result,
            "temporal": temporal_result,
            "behavioral": behavioral_result,
            "network": network_result,
            "process": process_result,
            **detection_result,
        }

    @staticmethod
    def _system_temporal_features(
        current: dict[str, float],
        previous: dict[str, float],
    ) -> dict[str, float]:
        """
        Calculate changes between current and previous
        system observations.
        """

        return {
            key: current[key] - previous[key]
            for key in current
            if key in previous
        }