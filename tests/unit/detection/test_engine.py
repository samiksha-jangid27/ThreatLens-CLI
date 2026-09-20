from threatlens.detection.engine import DetectionEngine


def test_engine_combines_detection_signals():
    engine = DetectionEngine()

    result = engine.analyze(
        {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": False,
            "process_anomaly": True,
        }
    )

    assert result["is_suspicious"] is True

    assert result["correlation"]["signal_count"] == 3

    assert result["risk"]["risk_score"] == 80.0

    assert result["risk"]["severity"] == "CRITICAL"


def test_engine_handles_single_signal():
    engine = DetectionEngine()

    result = engine.analyze(
        {
            "isolation_forest": True,
            "temporal_anomaly": False,
            "network_anomaly": False,
            "process_anomaly": False,
        }
    )

    assert result["is_suspicious"] is False

    assert result["correlation"]["signal_count"] == 1

    assert result["risk"]["risk_score"] == 40.0

    assert result["risk"]["severity"] == "MEDIUM"


def test_engine_handles_no_signals():
    engine = DetectionEngine()

    result = engine.analyze(
        {
            "isolation_forest": False,
            "temporal_anomaly": False,
            "network_anomaly": False,
            "process_anomaly": False,
        }
    )

    assert result["is_suspicious"] is False

    assert result["correlation"]["signal_count"] == 0

    assert result["risk"]["risk_score"] == 0.0

    assert result["risk"]["severity"] == "LOW"


def test_engine_preserves_signal_information():
    engine = DetectionEngine()

    signals = {
        "isolation_forest": True,
        "temporal_anomaly": False,
        "network_anomaly": True,
        "process_anomaly": False,
    }

    result = engine.analyze(signals)

    assert result["signals"] == signals

    assert result["correlation"]["triggered_signals"] == [
        "isolation_forest",
        "network_anomaly",
    ]
