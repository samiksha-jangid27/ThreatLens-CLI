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
    )

    previous = make_telemetry(
        20.0,
        40.0,
        1.0,
        100,
        50.0,
    )

    current = make_telemetry(
        22.0,
        41.0,
        1.1,
        101,
        50.0,
    )

    result = pipeline.scan(
        current=current,
        previous=previous,
    )

    assert "model" in result
    assert "temporal" in result
    assert "signals" in result
    assert "correlation" in result
    assert "risk" in result
    assert "is_suspicious" in result


def test_pipeline_detects_temporal_anomaly():
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
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 101.0,
            "uptime_seconds": 10001.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 19.0,
            "memory_percent": 39.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 99.0,
            "uptime_seconds": 10002.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10003.0,
            "disk_percent": 50.0,
        },
        {
            "cpu_percent": 21.0,
            "memory_percent": 41.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 101.0,
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
        20.0,
        40.0,
        1.0,
        100,
        50.0,
    )

    current = make_telemetry(
        80.0,
        75.0,
        5.0,
        180,
        70.0,
    )

    result = pipeline.scan(
        current=current,
        previous=previous,
    )

    assert result["temporal"]["is_anomaly"] is True

    assert (
        result["temporal"]["signal_count"]
        > 0
    )


def test_pipeline_accepts_network_and_process_signals():
    baseline = [
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10000.0,
            "disk_percent": 50.0,
        }
        for _ in range(5)
    ]

    detector = IsolationForestDetector(
        contamination=0.2,
        random_state=42,
    )

    detector.fit(baseline)

    pipeline = ThreatScanPipeline(
        isolation_forest=detector,
    )

    previous = make_telemetry(
        20.0,
        40.0,
        1.0,
        100,
        50.0,
    )

    current = make_telemetry(
        21.0,
        41.0,
        1.1,
        101,
        50.0,
    )

    previous_network = {
        "connection_count": 5,
        "tcp_connection_count": 4,
        "udp_connection_count": 1,
        "listening_port_count": 1,
        "connections": [],
    }

    current_network = {
        "connection_count": 20,
        "tcp_connection_count": 18,
        "udp_connection_count": 2,
        "listening_port_count": 4,
        "connections": [],
    }

    previous_processes = {
        "process_count": 100,
        "processes": [],
    }

    current_processes = {
        "process_count": 120,
        "processes": [],
    }

    result = pipeline.scan(
        current=current,
        previous=previous,
        current_network=current_network,
        previous_network=previous_network,
        current_processes=current_processes,
        previous_processes=previous_processes,
    )

    assert result["network"] is not None
    assert result["process"] is not None

    assert (
        "network_anomaly"
        in result["signals"]
    )

    assert (
        "process_anomaly"
        in result["signals"]
    )


def test_pipeline_uses_behavioral_baseline():
    baseline = [
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
            "uptime_seconds": 10000.0,
            "disk_percent": 50.0,
        }
        for _ in range(5)
    ]

    detector = IsolationForestDetector(
        contamination=0.2,
        random_state=42,
    )

    detector.fit(baseline)

    pipeline = ThreatScanPipeline(
        isolation_forest=detector,
    )

    previous = make_telemetry(
        20.0,
        40.0,
        1.0,
        100,
        50.0,
    )

    current = make_telemetry(
        80.0,
        75.0,
        5.0,
        180,
        70.0,
    )

    result = pipeline.scan(
        current=current,
        previous=previous,
        baseline=baseline,
    )

    assert result["behavioral"] is not None

    assert (
        "behavioral_deviation"
        in result["signals"]
    )

    assert (
        result["behavioral"]["is_anomaly"]
        is True
    )