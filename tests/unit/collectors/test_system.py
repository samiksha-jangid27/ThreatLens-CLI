from datetime import datetime

from threatlens.collectors.system import collect_system_telemetry
from threatlens.schema.telemetry import SystemTelemetry


def test_collect_system_telemetry():
    telemetry = collect_system_telemetry()

    assert isinstance(telemetry, SystemTelemetry)
    assert isinstance(telemetry.timestamp, datetime)

    assert 0 <= telemetry.cpu_percent <= 100
    assert 0 <= telemetry.memory_percent <= 100
    assert telemetry.memory_available_mb >= 0
    assert telemetry.load_average_1m >= 0
    assert telemetry.process_count > 0
    assert telemetry.uptime_seconds > 0
    assert 0 <= telemetry.disk_percent <= 100


def test_system_telemetry_to_dict():
    telemetry = collect_system_telemetry()

    data = telemetry.to_dict()

    assert isinstance(data, dict)
    assert isinstance(data["timestamp"], str)
    assert data["process_count"] > 0