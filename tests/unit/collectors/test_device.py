from types import SimpleNamespace

import psutil
import pytest

from threatlens.collectors.device import collect_device_observation
from threatlens.collectors.network import collect_network_telemetry
from threatlens.collectors.processes import collect_process_telemetry


def test_local_adapter_returns_valid_aggregate_sources(fake_host):
    result = collect_device_observation("lab")
    assert set(result.sources) == {"system", "network", "process"}
    assert result.sources["process"]["average_cpu_percent"] == 12.5
    assert "uptime_seconds" not in result.sources["system"]
    assert not result.unavailable


def test_denied_source_does_not_prevent_other_source_assessment(fake_host, monkeypatch):
    def denied():
        raise PermissionError("OS denied process listing")

    monkeypatch.setattr(psutil, "pids", denied)
    result = collect_device_observation("lab")
    assert "system" not in result.sources
    assert "system" in result.unavailable
    assert result.sources["network"]["connection_count"] == 0


def test_no_telemetry_is_an_explicit_error(monkeypatch):
    def denied():
        raise PermissionError("OS denied access")

    for name in (
        "collect_system_telemetry",
        "collect_network_telemetry",
        "collect_process_telemetry",
    ):
        monkeypatch.setattr("threatlens.collectors.device." + name, denied)
    with pytest.raises(ValueError, match="No telemetry"):
        collect_device_observation("lab")


def test_process_cpu_is_primed_then_measured(fake_host, monkeypatch):
    calls = []

    def cpu(interval):
        calls.append(interval)
        return 0 if len(calls) == 1 else 77

    process = SimpleNamespace(
        cpu_percent=cpu,
        as_dict=lambda attrs: {
            "pid": 3,
            "name": "worker",
            "username": "user",
            "memory_percent": 2,
            "status": "running",
            "ppid": 1,
        },
    )
    monkeypatch.setattr(psutil, "process_iter", lambda: iter([process]))
    result = collect_process_telemetry()
    assert result["processes"][0]["cpu_percent"] == 77
    assert len(calls) == 2


def test_disappearing_process_is_not_complete_telemetry(fake_host, monkeypatch):
    def disappeared(interval):
        raise psutil.NoSuchProcess(1)

    monkeypatch.setattr(
        psutil, "process_iter", lambda: iter([SimpleNamespace(cpu_percent=disappeared)])
    )
    assert not collect_process_telemetry()["available"]


def test_connection_counts_and_endpoints_are_extracted(monkeypatch):
    local = SimpleNamespace(ip="127.0.0.1", port=8080)
    remote = SimpleNamespace(ip="192.0.2.1", port=443)
    rows = [
        SimpleNamespace(laddr=local, raddr=remote, type=1, status="ESTABLISHED"),
        SimpleNamespace(laddr=local, raddr=(), type=2, status="NONE"),
        SimpleNamespace(laddr=local, raddr=(), type=1, status="LISTEN"),
    ]
    monkeypatch.setattr(psutil, "net_connections", lambda kind: rows)
    result = collect_network_telemetry()
    assert result.tcp_connection_count == 2
    assert result.udp_connection_count == 1
    assert result.listening_port_count == 1
    assert result.connections[0].remote_address == "192.0.2.1"
