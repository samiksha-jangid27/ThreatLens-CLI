"""Tests must never read or overwrite the developer's real monitoring state."""

import pytest


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch, tmp_path):
    monkeypatch.setenv("THREATLENS_DATA_DIR", str(tmp_path / "state"))


@pytest.fixture
def fake_host(monkeypatch):
    """Controlled host, independent of OS permissions or the developer's workload."""
    from types import SimpleNamespace
    import psutil
    import time

    monkeypatch.setattr(psutil, "pids", lambda: [1, 2, 3])
    monkeypatch.setattr(psutil, "virtual_memory", lambda: SimpleNamespace(percent=40, available=8000 * 1024**2))
    monkeypatch.setattr(psutil, "disk_usage", lambda path: SimpleNamespace(percent=50))
    monkeypatch.setattr(psutil, "getloadavg", lambda: (1, 1, 1))
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval: 20)
    monkeypatch.setattr(psutil, "boot_time", lambda: time.time() - 10000)
    monkeypatch.setattr(psutil, "net_connections", lambda kind: [])
    process = SimpleNamespace(cpu_percent=lambda interval: 12.5,
                              as_dict=lambda attrs: {"pid": 1, "name": "test", "username": "user", "memory_percent": 1, "status": "running", "ppid": 0})
    monkeypatch.setattr(psutil, "process_iter", lambda: iter([process]))
    monkeypatch.setattr("threatlens.collectors.processes.time.sleep", lambda seconds: None)
