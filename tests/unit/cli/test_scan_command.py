"""Real CLI integration: no fake detector and no real host state."""

import json
from datetime import datetime, timedelta, timezone

from typer.testing import CliRunner

from threatlens.cli.app import app
from threatlens.cli.commands import scan as scan_module
from threatlens.schema.device import DeviceObservation

runner = CliRunner()


def write_input(tmp_path, start=0, count=30, cpu=20, traffic=100, filename="telemetry.json"):
    observations = []
    for n in range(start, start + count):
        observations.append({"timestamp": (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=n)).isoformat(),
                             "window_seconds": 60, "sources": {"system": {"cpu_percent": cpu}, "network": {"bytes_out": traffic}}, "unavailable": {}})
    path = tmp_path / filename
    path.write_text(json.dumps({"schema_version": 1, "device_id": "lab-router", "device_type": "router", "observations": observations}))
    return path


def test_learn_scan_explain_report_end_to_end(tmp_path):
    baseline = write_input(tmp_path)
    learned = runner.invoke(app, ["learn", "--input", str(baseline), "--json"])
    assert learned.exit_code == 0, learned.output
    assert json.loads(learned.stdout)["ready"]
    suspicious = write_input(tmp_path, 30, 1, 95, 10000)
    result = runner.invoke(app, ["scan", "--input", str(suspicious), "--json", "--fail-on-alert"])
    assert result.exit_code == 3, result.output
    incident_id = json.loads(result.stdout)["results"][0]["incident_id"]
    explained = runner.invoke(app, ["explain", str(incident_id), "--json"])
    assert explained.exit_code == 0
    evidence = json.loads(explained.stdout)["evidence"]
    assert any(row["details"].get("current") == 10000 for row in evidence)
    report = tmp_path / "report.json"
    generated = runner.invoke(app, ["report", "--format", "json", "--output", str(report)])
    assert generated.exit_code == 0, generated.output
    assert json.loads(report.read_text())["incidents"][0]["features"]["network"]["bytes_out"] == 10000


def test_untrained_scan_reports_insufficient_evidence(tmp_path):
    data = write_input(tmp_path, count=1)
    result = runner.invoke(app, ["scan", "--input", str(data), "--json"])
    assert result.exit_code == 4
    assert json.loads(result.stdout)["results"][0]["status"] == "INSUFFICIENT_BASELINE"


def test_malformed_input_has_clean_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{broken")
    result = runner.invoke(app, ["scan", "--input", str(path), "--json"])
    assert result.exit_code == 2
    assert "ThreatLens:" in result.output
    assert "Traceback" not in result.output


def test_local_scan_collects_once(monkeypatch):
    calls = []
    def collect(device_id):
        calls.append(device_id)
        return DeviceObservation("local", "system", "2026-01-01T00:00:00Z", 1, {"system": {"cpu_percent": 20}}, {})
    monkeypatch.setattr(scan_module, "collect_device_observation", collect)
    result = runner.invoke(app, ["scan", "--json"])
    assert result.exit_code == 4
    assert len(calls) == 1


def test_status_reports_readiness(tmp_path):
    result = runner.invoke(app, ["status", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["devices"] == []
