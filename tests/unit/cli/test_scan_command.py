import json

from typer.testing import CliRunner

from threatlens.cli.app import app
from threatlens.cli.commands import scan as scan_module
from datetime import datetime, timezone
from threatlens.schema.network import NetworkTelemetry
runner = CliRunner()


def make_telemetry(values: dict):
    return type(
        "Telemetry",
        (),
        {
            "to_dict": lambda self: values,
            "timestamp": type(
                "Timestamp",
                (),
                {
                    "isoformat": lambda self: (
                        "2026-09-20T18:00:00+00:00"
                    )
                },
            )(),
        },
    )()


def make_network_telemetry():
    return NetworkTelemetry(
        timestamp=datetime(
            2026,
            9,
            20,
            18,
            0,
            tzinfo=timezone.utc,
        ),
        connection_count=5,
        tcp_connection_count=4,
        udp_connection_count=1,
        listening_port_count=1,
        connections=(),
    )


def make_process_telemetry():
    return {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "process_count": 100,
        "processes": [],
    }


def make_normal_baseline():
    return {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "memory_available_mb": 8000.0,
        "load_average_1m": 1.0,
        "process_count": 100,
        "uptime_seconds": 10000,
        "disk_percent": 50.0,
    }


def test_scan_builds_baseline(
    monkeypatch,
    tmp_path,
):
    baseline_path = (
        tmp_path / "system_baseline.json"
    )

    network_baseline_path = (
        tmp_path / "network_baseline.json"
    )

    process_baseline_path = (
        tmp_path / "process_baseline.json"
    )

    monkeypatch.setattr(
        scan_module,
        "BASELINE_PATH",
        baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "NETWORK_BASELINE_PATH",
        network_baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "PROCESS_BASELINE_PATH",
        process_baseline_path,
    )

    telemetry = {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "memory_available_mb": 8000.0,
        "load_average_1m": 1.0,
        "process_count": 100,
        "uptime_seconds": 10000,
        "disk_percent": 50.0,
    }

    monkeypatch.setattr(
        scan_module,
        "collect_system_telemetry",
        lambda: make_telemetry(telemetry),
    )

    monkeypatch.setattr(
        scan_module,
        "collect_network_telemetry",
        make_network_telemetry,
    )

    monkeypatch.setattr(
        scan_module,
        "collect_process_telemetry",
        make_process_telemetry,
    )

    result = runner.invoke(
        app,
        ["scan"],
    )

    assert result.exit_code == 0

    assert (
        "system observations: 1/5"
        in result.stdout.lower()
    )

    assert (
        "network observations: 1/5"
        in result.stdout.lower()
    )

    assert (
        "process observations: 1/5"
        in result.stdout.lower()
    )

    assert baseline_path.exists()
    assert network_baseline_path.exists()
    assert process_baseline_path.exists()

    system_data = json.loads(
        baseline_path.read_text(
            encoding="utf-8"
        )
    )

    network_data = json.loads(
        network_baseline_path.read_text(
            encoding="utf-8"
        )
    )

    process_data = json.loads(
        process_baseline_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(system_data) == 1
    assert len(network_data) == 1
    assert len(process_data) == 1


def test_scan_detects_after_baseline(
    monkeypatch,
    tmp_path,
):
    baseline_path = (
        tmp_path / "system_baseline.json"
    )

    network_baseline_path = (
        tmp_path / "network_baseline.json"
    )

    process_baseline_path = (
        tmp_path / "process_baseline.json"
    )

    normal = make_normal_baseline()

    baseline_path.write_text(
        json.dumps([normal] * 5),
        encoding="utf-8",
    )

    network_observation = {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "connection_count": 5,
        "tcp_connection_count": 4,
        "udp_connection_count": 1,
        "listening_port_count": 1,
        "connections": [],
    }

    network_baseline_path.write_text(
        json.dumps([network_observation] * 5),
        encoding="utf-8",
    )

    process_observation = {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "process_count": 100,
        "processes": [],
    }

    process_baseline_path.write_text(
        json.dumps([process_observation] * 5),
        encoding="utf-8",
    )

    telemetry = {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "cpu_percent": 80.0,
        "memory_percent": 75.0,
        "memory_available_mb": 2000.0,
        "load_average_1m": 5.0,
        "process_count": 180,
        "uptime_seconds": 10000,
        "disk_percent": 70.0,
    }

    monkeypatch.setattr(
        scan_module,
        "BASELINE_PATH",
        baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "NETWORK_BASELINE_PATH",
        network_baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "PROCESS_BASELINE_PATH",
        process_baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "collect_system_telemetry",
        lambda: make_telemetry(telemetry),
    )

    monkeypatch.setattr(
        scan_module,
        "collect_network_telemetry",
        make_network_telemetry,
    )

    monkeypatch.setattr(
        scan_module,
        "collect_process_telemetry",
        make_process_telemetry,
    )

    result = runner.invoke(
        app,
        ["scan"],
    )

    assert result.exit_code == 0

    assert (
        "threatlens scan"
        in result.stdout.lower()
    )

    assert (
        "status:"
        in result.stdout.lower()
    )


def test_suspicious_scan_creates_incident(
    monkeypatch,
    tmp_path,
):
    baseline_path = (
        tmp_path / "system_baseline.json"
    )

    network_baseline_path = (
        tmp_path / "network_baseline.json"
    )

    process_baseline_path = (
        tmp_path / "process_baseline.json"
    )

    database_path = (
        tmp_path / "threatlens.db"
    )

    normal = make_normal_baseline()

    baseline = [normal] * 5

    network_observation = {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "connection_count": 5,
        "tcp_connection_count": 4,
        "udp_connection_count": 1,
        "listening_port_count": 1,
        "connections": [],
    }

    process_observation = {
        "timestamp": "2026-09-20T18:00:00+00:00",
        "process_count": 100,
        "processes": [],
    }

    network_baseline_path.write_text(
        json.dumps([network_observation] * 5),
        encoding="utf-8",
    )

    process_baseline_path.write_text(
        json.dumps([process_observation] * 5),
        encoding="utf-8",
    )

    telemetry = make_telemetry(
        {
            "timestamp": (
                "2026-09-20T18:00:00+00:00"
            ),
            "cpu_percent": 90.0,
            "memory_percent": 90.0,
            "memory_available_mb": 1000.0,
            "load_average_1m": 8.0,
            "process_count": 200,
            "uptime_seconds": 10000,
            "disk_percent": 80.0,
        }
    )

    monkeypatch.setattr(
        scan_module,
        "BASELINE_PATH",
        baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "NETWORK_BASELINE_PATH",
        network_baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "PROCESS_BASELINE_PATH",
        process_baseline_path,
    )

    monkeypatch.setattr(
        scan_module,
        "collect_system_telemetry",
        lambda: telemetry,
    )

    monkeypatch.setattr(
        scan_module,
        "collect_network_telemetry",
        make_network_telemetry,
    )

    monkeypatch.setattr(
        scan_module,
        "collect_process_telemetry",
        make_process_telemetry,
    )

    monkeypatch.setattr(
        scan_module,
        "DATABASE_PATH",
        database_path,
    )

    class FakePipeline:
        def scan(
            self,
            current,
            previous,
            current_network=None,
            previous_network=None,
            current_processes=None,
            previous_processes=None,
        ):
            return {
                "model": {
                    "is_anomaly": True,
                    "anomaly_score": -0.2,
                },
                "temporal": {
                    "is_anomaly": True,
                    "signal_count": 3,
                },
                "signals": {
                    "isolation_forest": True,
                    "temporal_anomaly": True,
                    "network_anomaly": True,
                    "process_anomaly": True,
                },
                "correlation": {
                    "is_correlated": True,
                    "signal_count": 4,
                    "triggered_signals": [
                        "isolation_forest",
                        "temporal_anomaly",
                        "network_anomaly",
                        "process_anomaly",
                    ],
                },
                "risk": {
                    "risk_score": 65.0,
                    "severity": "HIGH",
                    "triggered_signals": [
                        "isolation_forest",
                        "temporal_anomaly",
                    ],
                },
                "is_suspicious": True,
            }

    monkeypatch.setattr(
        scan_module,
        "ThreatScanPipeline",
        lambda isolation_forest: FakePipeline(),
    )

    monkeypatch.setattr(
        scan_module,
        "_load_baseline",
        lambda: baseline,
    )

    result = runner.invoke(
        app,
        ["scan"],
    )

    assert result.exit_code == 0

    assert (
        "incident created"
        in result.stdout.lower()
    )

    repository = (
        scan_module._get_repository()
    )

    incidents = repository.list_all()

    assert len(incidents) == 1

    assert (
        incidents[0]["risk_score"]
        == 65.0
    )

    assert (
        incidents[0]["severity"]
        == "HIGH"
    )