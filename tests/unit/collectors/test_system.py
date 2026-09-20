from threatlens.collectors.system import collect_system_telemetry


def test_collect_system_telemetry():
    telemetry = collect_system_telemetry()

    expected_keys = {
        "timestamp",
        "cpu_percent",
        "memory_percent",
        "memory_available_mb",
        "load_average_1m",
        "process_count",
        "uptime_seconds",
        "disk_percent",
    }

    assert expected_keys.issubset(telemetry.keys())

    assert 0 <= telemetry["cpu_percent"] <= 100
    assert 0 <= telemetry["memory_percent"] <= 100
    assert telemetry["memory_available_mb"] >= 0
    assert telemetry["load_average_1m"] >= 0
    assert telemetry["process_count"] > 0
    assert telemetry["uptime_seconds"] > 0
    assert 0 <= telemetry["disk_percent"] <= 100