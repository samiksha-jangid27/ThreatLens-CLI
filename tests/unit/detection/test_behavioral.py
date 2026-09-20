import pytest

from threatlens.detection.behavioral import (
    BehavioralDeviationDetector,
)


def test_detector_finds_large_deviation():
    detector = BehavioralDeviationDetector(
        threshold=3.0
    )

    baseline = [
        {"cpu_percent": 20.0},
        {"cpu_percent": 21.0},
        {"cpu_percent": 19.0},
        {"cpu_percent": 20.0},
        {"cpu_percent": 21.0},
    ]

    result = detector.analyze(
        {"cpu_percent": 80.0},
        baseline,
    )

    assert result["is_anomaly"] is True

    assert (
        "cpu_percent"
        in result["anomalous_features"]
    )


def test_detector_accepts_normal_behavior():
    detector = BehavioralDeviationDetector(
        threshold=3.0
    )

    baseline = [
        {"cpu_percent": 20.0},
        {"cpu_percent": 21.0},
        {"cpu_percent": 19.0},
        {"cpu_percent": 20.0},
        {"cpu_percent": 21.0},
    ]

    result = detector.analyze(
        {"cpu_percent": 20.0},
        baseline,
    )

    assert result["is_anomaly"] is False

    assert result["anomalous_features"] == []


def test_detector_returns_z_score():
    detector = BehavioralDeviationDetector(
        threshold=3.0
    )

    baseline = [
        {"cpu_percent": 20.0},
        {"cpu_percent": 20.0},
        {"cpu_percent": 20.0},
        {"cpu_percent": 20.0},
        {"cpu_percent": 20.0},
    ]

    result = detector.analyze(
        {"cpu_percent": 25.0},
        baseline,
    )

    assert (
        "cpu_percent"
        in result["signals"]
    )

    assert (
        result["signals"]["cpu_percent"]["z_score"]
        > 0
    )


def test_detector_requires_baseline():
    detector = BehavioralDeviationDetector()

    with pytest.raises(ValueError):
        detector.analyze(
            {"cpu_percent": 20.0},
            [],
        )


def test_detector_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        BehavioralDeviationDetector(
            threshold=0
        )
