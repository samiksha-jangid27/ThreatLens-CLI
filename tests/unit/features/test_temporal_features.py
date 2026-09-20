from threatlens.features.temporal import (
    calculate_change,
    extract_temporal_features,
)


def test_calculate_change():
    assert calculate_change(80, 50) == 30
    assert calculate_change(40, 50) == -10


def test_extract_temporal_features():
    previous = {
        "cpu_percent": 20,
        "memory_percent": 50,
        "load_average_1m": 1.5,
        "process_count": 100,
        "disk_percent": 40,
    }

    current = {
        "cpu_percent": 70,
        "memory_percent": 65,
        "load_average_1m": 3.0,
        "process_count": 120,
        "disk_percent": 41,
    }

    features = extract_temporal_features(
        current,
        previous,
    )

    assert features["cpu_delta"] == 50
    assert features["memory_delta"] == 15
    assert features["load_delta"] == 1.5
    assert features["process_delta"] == 20
    assert features["disk_delta"] == 1