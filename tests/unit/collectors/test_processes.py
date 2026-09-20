from threatlens.collectors.processes import collect_process_telemetry
from threatlens.schema.process import ProcessTelemetry


def test_process_schema_serializes_correctly():
    process = ProcessTelemetry(
        pid=1234,
        name="python",
        username="test-user",
        cpu_percent=12.5,
        memory_percent=4.2,
        status="running",
        parent_pid=1000,
    )

    result = process.to_dict()

    assert result["pid"] == 1234
    assert result["name"] == "python"
    assert result["username"] == "test-user"
    assert result["cpu_percent"] == 12.5
    assert result["memory_percent"] == 4.2
    assert result["status"] == "running"
    assert result["parent_pid"] == 1000


def test_process_collector_returns_expected_structure():
    result = collect_process_telemetry()

    assert "timestamp" in result
    assert "process_count" in result
    assert "processes" in result

    assert result["process_count"] >= 0
    assert isinstance(result["processes"], list)


def test_collected_processes_have_expected_fields():
    result = collect_process_telemetry()

    for process in result["processes"]:
        assert "pid" in process
        assert "name" in process
        assert "username" in process
        assert "cpu_percent" in process
        assert "memory_percent" in process
        assert "status" in process
        assert "parent_pid" in process

        assert process["pid"] >= 0
        assert process["cpu_percent"] >= 0
        assert process["memory_percent"] >= 0