from threatlens.collectors.system import collect_system_telemetry
from threatlens.features.system import extract_system_features
from threatlens.ingestion.normalizer import normalize_system_telemetry


def test_extract_system_features(fake_host):
    telemetry = collect_system_telemetry()
    normalized = normalize_system_telemetry(telemetry)

    features = extract_system_features(normalized)

    expected = {
        "cpu_percent",
        "memory_percent",
        "memory_available_mb",
        "load_average_1m",
        "process_count",
        "disk_percent",
    }

    assert set(features.keys()) == expected

    for value in features.values():
        assert isinstance(value, float)
