from datetime import datetime, timezone

from threatlens.detection.pipeline import ThreatScanPipeline
from threatlens.detection.temporal import TemporalAnomalyDetector
from threatlens.models.isolation_forest import IsolationForestDetector
from threatlens.schema.telemetry import SystemTelemetry


def make_telemetry(
    cpu: float,
    memory: float,
    load: float,
    processes: int,
    disk: float,
) -> SystemTelemetry:
    return SystemTelemetry(
        timestamp=datetime.now(timezone.utc),
        cpu_percent=cpu,
        memory_percent=memory,
        memory_available_mb=8000.0,
        load_average_1m=load,
        process_count=processes,
        uptime_seconds=10000,
        disk_percent=disk,
    )


def test_pipeline_returns_detection_result():
    baseline = [
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10000.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 22.0,
            "memory_percent": 41.0,
            "memory_available_mb": 7900.0,
            "load_average_1m": 1.1,
            "process_count": 101.0,
            "uptime_seconds": 10001.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 21.0,
            "memory_percent": 39.0,
            "memory_available_mb": 8100.0,
            "load_average_1m": 0.9,
            "process_count": 99.0,
            "uptime_seconds": 10002.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 23.0,
            "memory_percent": 42.0,
            "memory_available_mb": 7800.0,
            "load_average_1m": 1.2,
            "process_count": 102.0,
            "uptime_seconds": 10003.0,
            "disk_percent": 51.0,
        },
        {
            "cpu_percent": 19.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8200.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10004.0,
            "disk_percent": 50.0,
        },
    ]

    detector = IsolationForestDetector(
        contamination=0.2,
        random_state=42,
    )

    detector.fit(baseline)

    pipeline = ThreatScanPipeline(
        isolation_forest=detector,
        temporal_detector=TemporalAnomalyDetector(),
    )

    previous = make_telemetry(
        cpu=21.0,
        memory=40.0,
        load=1.0,
        processes=100,
        disk=50.0,
    )

    current = make_telemetry(
        cpu=85.0,
        memory=80.0,
        load=5.0,
        processes=180,
        disk=70.0,
    )

    result = pipeline.scan(
        current=current,
        previous=previous,
    )

    assert "model" in result
    assert "temporal" in result
    assert "risk" in result
    assert "correlation" in result
    assert "signals" in result
    assert "is_suspicious" in result


def test_pipeline_detects_temporal_anomaly():
    detector = IsolationForestDetector(
        contamination=0.2,
        random_state=42,
    )

    baseline = [
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10000.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 21.0,
            "memory_percent": 41.0,
            "memory_available_mb": 7900.0,
            "load_average_1m": 1.1,
            "process_count": 101.0,
            "uptime_seconds": 10001.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 22.0,
            "memory_percent": 39.0,
            "memory_available_mb": 8100.0,
            "load_average_1m": 0.9,
            "process_count": 99.0,
            "uptime_seconds": 10002.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 23.0,
            "memory_percent": 42.0,
            "memory_available_mb": 7800.0,
            "load_average_1m": 1.2,
            "process_count": 102.0,
            "uptime_seconds": 10003.0,
            "disk_percent": 51.0,
        },
        {
            "cpu_percent": 19.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8200.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10004.0,
            "disk_percent": 50.0,
        },
    ]

    detector.fit(baseline)

    pipeline = ThreatScanPipeline(
        isolation_forest=detector,
    )

    previous = make_telemetry(
        cpu=20.0,
        memory=40.0,
        load=1.0,
        processes=100,
        disk=50.0,
    )

    current = make_telemetry(
        cpu=80.0,
        memory=75.0,
        load=4.0,
        processes=180,
        disk=65.0,
    )

    result = pipeline.scan(
        current=current,
        previous=previous,
    )

    assert result["temporal"]["is_anomaly"] is True
    assert result["temporal"]["signal_count"] > 0
