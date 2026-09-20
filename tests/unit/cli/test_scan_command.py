import json

from typer.testing import CliRunner

from threatlens.cli.app import app
from threatlens.cli.commands import scan as scan_module


runner = CliRunner()


def test_scan_builds_baseline(monkeypatch, tmp_path):
    baseline_path = tmp_path / "system_baseline.json"

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
        lambda: type(
            "Telemetry",
            (),
            {"to_dict": lambda self: telemetry},
        )(),
    )

    result = runner.invoke(
        app,
        ["scan"],
    )

    assert result.exit_code == 0
    assert "baseline observation 1/5" in result.stdout.lower()

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
    baseline_path = tmp_path / "system_baseline.json"

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
        lambda: type(
            "Telemetry",
            (),
            {"to_dict": lambda self: telemetry},
        )(),
    )

    result = runner.invoke(
        app,
        ["scan"],
    )

    assert result.exit_code == 0
    assert "threatlens scan" in result.stdout.lower()
    assert "anomaly score" in result.stdout.lower()
