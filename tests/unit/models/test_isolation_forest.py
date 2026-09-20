import pytest

from threatlens.models.isolation_forest import (
    IsolationForestDetector,
)


def training_data():
    return [
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
        },
        {
            "cpu_percent": 22.0,
            "memory_percent": 42.0,
            "load_average_1m": 1.1,
            "process_count": 102.0,
        },
        {
            "cpu_percent": 19.0,
            "memory_percent": 39.0,
            "load_average_1m": 0.9,
            "process_count": 98.0,
        },
        {
            "cpu_percent": 21.0,
            "memory_percent": 41.0,
            "load_average_1m": 1.0,
            "process_count": 101.0,
        },
        {
            "cpu_percent": 23.0,
            "memory_percent": 43.0,
            "load_average_1m": 1.2,
            "process_count": 103.0,
        },
        {
            "cpu_percent": 18.0,
            "memory_percent": 38.0,
            "load_average_1m": 0.8,
            "process_count": 97.0,
        },
        {
            "cpu_percent": 24.0,
            "memory_percent": 44.0,
            "load_average_1m": 1.3,
            "process_count": 104.0,
        },
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
        },
        {
            "cpu_percent": 21.0,
            "memory_percent": 41.0,
            "load_average_1m": 1.1,
            "process_count": 101.0,
        },
        {
            "cpu_percent": 22.0,
            "memory_percent": 42.0,
            "load_average_1m": 1.1,
            "process_count": 102.0,
        },
    ]


def test_detector_fits():
    detector = IsolationForestDetector(
        contamination=0.1,
        random_state=42,
    )

    detector.fit(training_data())

    assert detector.is_fitted is True

    assert detector.feature_names == [
        "cpu_percent",
        "memory_percent",
        "load_average_1m",
        "process_count",
    ]


def test_detector_predicts_normal_observation():
    detector = IsolationForestDetector(
        contamination=0.1,
        random_state=42,
    )

    detector.fit(training_data())

    result = detector.predict(
        {
            "cpu_percent": 21.0,
            "memory_percent": 41.0,
            "load_average_1m": 1.0,
            "process_count": 100.0,
        }
    )

    assert isinstance(result["is_anomaly"], bool)
    assert result["prediction"] in (-1, 1)
    assert isinstance(result["anomaly_score"], float)


def test_detector_rejects_prediction_before_training():
    detector = IsolationForestDetector()

    with pytest.raises(RuntimeError):
        detector.predict(
            {
                "cpu_percent": 20.0,
                "memory_percent": 40.0,
                "load_average_1m": 1.0,
                "process_count": 100.0,
            }
        )


def test_detector_rejects_empty_training_data():
    detector = IsolationForestDetector()

    with pytest.raises(ValueError):
        detector.fit([])
