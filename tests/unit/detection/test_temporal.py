from threatlens.detection.temporal import (
    TemporalAnomalyDetector,
)


def test_detects_sudden_behavior_change():
    detector = TemporalAnomalyDetector()

    previous = {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.0,
        "process_count": 100.0,
        "disk_percent": 40.0,
    }

    current = {
        "cpu_percent": 80.0,
        "memory_percent": 45.0,
        "load_average_1m": 1.5,
        "process_count": 110.0,
        "disk_percent": 41.0,
    }

    result = detector.analyze(
        current,
        previous,
    )

    assert result["is_anomaly"] is True
    assert result["signal_count"] == 1

    assert result["triggered_signals"]["cpu_percent"] == 60.0


def test_normal_change_is_not_anomaly():
    detector = TemporalAnomalyDetector()

    previous = {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.0,
        "process_count": 100.0,
        "disk_percent": 40.0,
    }

    current = {
        "cpu_percent": 25.0,
        "memory_percent": 45.0,
        "load_average_1m": 1.5,
        "process_count": 110.0,
        "disk_percent": 41.0,
    }

    result = detector.analyze(
        current,
        previous,
    )

    assert result["is_anomaly"] is False
    assert result["signal_count"] == 0
    assert result["triggered_signals"] == {}


def test_detects_multiple_changes():
    detector = TemporalAnomalyDetector()

    previous = {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.0,
        "process_count": 100.0,
        "disk_percent": 40.0,
    }

    current = {
        "cpu_percent": 80.0,
        "memory_percent": 75.0,
        "load_average_1m": 5.0,
        "process_count": 180.0,
        "disk_percent": 41.0,
    }

    result = detector.analyze(
        current,
        previous,
    )

    assert result["is_anomaly"] is True
    assert result["signal_count"] == 4

    assert "cpu_percent" in result["triggered_signals"]
    assert "memory_percent" in result["triggered_signals"]
    assert "load_average_1m" in result["triggered_signals"]
    assert "process_count" in result["triggered_signals"]


def test_negative_change_is_detected():
    detector = TemporalAnomalyDetector()

    previous = {
        "cpu_percent": 80.0,
        "memory_percent": 80.0,
        "load_average_1m": 5.0,
        "process_count": 200.0,
        "disk_percent": 40.0,
    }

    current = {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.0,
        "process_count": 100.0,
        "disk_percent": 41.0,
    }

    result = detector.analyze(
        current,
        previous,
    )

    assert result["is_anomaly"] is True
    assert result["signal_count"] == 4
