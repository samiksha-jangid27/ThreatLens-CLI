import json

from typer.testing import CliRunner

from threatlens.cli.app import app
from threatlens.cli.commands import scan as scan_module


runner = CliRunner()


def make_telemetry(values: dict):
    """Create a lightweight fake telemetry object."""

    return type(
        "Telemetry",
        (),
        {
            "to_dict": lambda self: values,
            "timestamp": type(
                "Timestamp",
                (),
                {
                    "isoformat": lambda self:
                    "2026-09-20T18:00:00+00:00"
                },
            )(),
        },
    )()


def test_scan_builds_baseline(
    monkeypatch,
    tmp_path,
):
    baseline_path = (
        tmp_path / "system_baseline.json"
    )

    monkeypatch.setattr(
        scan_module,
        "BASELINE_PATH",
        baseline_path,
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

    result = runner.invoke(
        app,
        ["scan"],
    )

    assert result.exit_code == 0

    assert (
        "baseline observation 1/5"
        in result.stdout.lower()
    )

    assert baseline_path.exists()

    saved = json.loads(
        baseline_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(saved) == 1


def test_scan_detects_after_baseline(
    monkeypatch,
    tmp_path,
):
    baseline_path = (
        tmp_path / "system_baseline.json"
    )

    normal = {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "memory_available_mb": 8000.0,
        "load_average_1m": 1.0,
        "process_count": 100,
        "uptime_seconds": 10000,
        "disk_percent": 50.0,
    }

    baseline_path.write_text(
        json.dumps([normal] * 5),
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
        "collect_system_telemetry",
        lambda: make_telemetry(telemetry),
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
        "anomaly score"
        in result.stdout.lower()
    )


def test_suspicious_scan_creates_incident(
    monkeypatch,
    tmp_path,
):
    database_path = (
        tmp_path / "threatlens.db"
    )

    telemetry = make_telemetry(
        {
            "timestamp":
            "2026-09-20T18:00:00+00:00",
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
        "collect_system_telemetry",
        lambda: telemetry,
    )

    monkeypatch.setattr(
        scan_module,
        "DATABASE_PATH",
        database_path,
    )

    class FakePipeline:
        def scan(self, current, previous):
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
                },
                "correlation": {
                    "is_correlated": True,
                    "signal_count": 2,
                    "triggered_signals": [
                        "isolation_forest",
                        "temporal_anomaly",
                    ],
                },
                "risk": {
                    "risk_score": 65.0,
                    "severity": "HIGH",
                },
                "is_suspicious": True,
            }

    monkeypatch.setattr(
        scan_module,
        "ThreatScanPipeline",
        lambda isolation_forest: FakePipeline(),
    )

    baseline = [
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
            "memory_available_mb": 8000.0,
            "load_average_1m": 1.0,
            "process_count": 100,
            "uptime_seconds": 10000,
            "disk_percent": 50.0,
        }
    ] * 5

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

    repository = scan_module._get_repository()
    incidents = repository.list_all()

    assert len(incidents) == 1
    assert incidents[0]["risk_score"] == 65.0
    assert incidents[0]["severity"] == "HIGH"