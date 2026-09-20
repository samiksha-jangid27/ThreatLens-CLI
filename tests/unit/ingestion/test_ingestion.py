from threatlens.collectors.system import collect_system_telemetry
from threatlens.ingestion.normalizer import normalize_system_telemetry
from threatlens.ingestion.validator import validate_system_telemetry


def test_normalize_system_telemetry():
    telemetry = collect_system_telemetry()

    data = normalize_system_telemetry(telemetry)

    assert isinstance(data, dict)
    assert isinstance(data["cpu_percent"], float)
    assert isinstance(data["memory_percent"], float)
    assert isinstance(data["process_count"], int)


def test_validate_system_telemetry():
    telemetry = collect_system_telemetry()

    data = normalize_system_telemetry(telemetry)

    validate_system_telemetry(data)


def test_validate_rejects_invalid_cpu():
    telemetry = collect_system_telemetry()
    data = normalize_system_telemetry(telemetry)

    data["cpu_percent"] = 101

    try:
        validate_system_telemetry(data)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected validation to reject invalid CPU value"
        )