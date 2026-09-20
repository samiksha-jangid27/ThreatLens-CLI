from typing import Any

from threatlens.detection.engine import DetectionEngine
from threatlens.detection.temporal import TemporalAnomalyDetector
from threatlens.features.system import extract_system_features
from threatlens.features.temporal import extract_temporal_features
from threatlens.ingestion.normalizer import normalize_system_telemetry
from threatlens.ingestion.validator import validate_system_telemetry
from threatlens.models.isolation_forest import IsolationForestDetector
from threatlens.schema.telemetry import SystemTelemetry


class ThreatScanPipeline:
    """Run the ThreatLens behavioral detection pipeline."""

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
    ) -> dict[str, Any]:
        """Analyze the current system state against a previous state."""

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

        temporal_features = extract_temporal_features(
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

        signals = {
            "isolation_forest": model_result["is_anomaly"],
            "temporal_anomaly": temporal_result["is_anomaly"],
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
            **detection_result,
        }
