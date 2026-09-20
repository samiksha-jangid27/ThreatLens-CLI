from typing import Any

from threatlens.detection.engine import DetectionEngine
from threatlens.detection.temporal import TemporalAnomalyDetector
from threatlens.features.network import extract_network_features
from threatlens.features.network_temporal import (
    extract_network_temporal_features,
)
from threatlens.features.process import extract_process_features
from threatlens.features.system import extract_system_features
from threatlens.ingestion.normalizer import normalize_system_telemetry
from threatlens.ingestion.validator import validate_system_telemetry
from threatlens.models.isolation_forest import IsolationForestDetector
from threatlens.schema.network import NetworkTelemetry
from threatlens.schema.process import ProcessTelemetry
from threatlens.schema.telemetry import SystemTelemetry


class ThreatScanPipeline:
    """Run the ThreatLens multi-signal behavioral pipeline."""

    def __init__(
        self,
        isolation_forest: IsolationForestDetector,
        temporal_detector: TemporalAnomalyDetector | None = None,
        detection_engine: DetectionEngine | None = None,
    ) -> None:
        self.isolation_forest = isolation_forest
        self.temporal_detector = (
            temporal_detector
            or TemporalAnomalyDetector()
        )
        self.detection_engine = (
            detection_engine
            or DetectionEngine()
        )

    def scan(
        self,
        current: SystemTelemetry,
        previous: SystemTelemetry,
        current_network: NetworkTelemetry | dict[str, Any] | None = None,
        previous_network: NetworkTelemetry | dict[str, Any] | None = None,
        current_processes: dict[str, Any] | None = None,
        previous_processes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze system, network, and process behavior."""

        current_normalized = normalize_system_telemetry(
            current
        )

        previous_normalized = normalize_system_telemetry(
            previous
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

        temporal_features = self._system_temporal_features(
            current_features,
            previous_features,
        )

        model_result = self.isolation_forest.predict(
            current_features
        )

        temporal_result = self.temporal_detector.analyze(
            current_features,
            previous_features,
        )

        signals: dict[str, bool] = {
            "isolation_forest": bool(
                model_result["is_anomaly"]
            ),
            "temporal_anomaly": bool(
                temporal_result["is_anomaly"]
            ),
        }

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

            network_anomaly = any(
                abs(value) >= 5.0
                for value in network_temporal.values()
            )

            signals["network_anomaly"] = network_anomaly

            network_result = {
                "features": current_network_features,
                "temporal_features": network_temporal,
                "is_anomaly": network_anomaly,
            }

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
                    current_process_features.get(key, 0.0)
                    - previous_process_features.get(key, 0.0)
                )
                for key in current_process_features
            }

            process_anomaly = any(
                abs(value) >= 10.0
                for value in process_deltas.values()
            )

            signals["process_anomaly"] = process_anomaly

            process_result = {
                "features": current_process_features,
                "deltas": process_deltas,
                "is_anomaly": process_anomaly,
            }

        detection_result = self.detection_engine.analyze(
            signals
        )

        return {
            "current": current_normalized,
            "previous": previous_normalized,
            "features": current_features,
            "temporal_features": temporal_features,
            "model": model_result,
            "temporal": temporal_result,
            "network": network_result,
            "process": process_result,
            **detection_result,
        }

    @staticmethod
    def _system_temporal_features(
        current: dict[str, float],
        previous: dict[str, float],
    ) -> dict[str, float]:
        """Calculate system feature deltas."""

        return {
            key: current[key] - previous[key]
            for key in current
            if key in previous
        }