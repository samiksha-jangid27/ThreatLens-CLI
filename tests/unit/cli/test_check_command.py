import json

from typer.testing import CliRunner

from threatlens.cli.app import app
from threatlens.cli.commands import check as check_module
from threatlens.config import database_path

runner = CliRunner()


def test_check_reads_live_metrics_without_creating_state(fake_host):
    result = runner.invoke(app, ["check", "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["data_origin"] == "live_local_telemetry"
    assert data["sources"]["system"]["cpu_percent"] == 20
    assert data["security_assessment"] == "NOT_PERFORMED"
    assert not database_path().exists()


def test_check_reports_denied_sources(fake_host, monkeypatch):
    def denied(kind):
        raise PermissionError("denied")

    monkeypatch.setattr("psutil.net_connections", denied)
    result = runner.invoke(app, ["check", "--json"])
    data = json.loads(result.stdout)
    assert result.exit_code == 0
    assert data["coverage"]["degraded"]
    assert "network" in data["coverage"]["unavailable_sources"]
    assert "network" not in data["sources"]


def test_check_terminal_displays_metrics(fake_host):
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
    assert "cpu_percent" in result.stdout
    assert "does not establish" in result.stdout


def test_check_saves_snapshot_and_refuses_overwrite(fake_host, tmp_path):
    path = tmp_path / "snapshot.json"
    assert runner.invoke(app, ["check", "--output", str(path)]).exit_code == 0
    saved = path.read_bytes()
    assert runner.invoke(app, ["check", "--output", str(path)]).exit_code == 2
    assert path.read_bytes() == saved


def test_no_telemetry_is_an_operational_error(monkeypatch):
    def denied():
        raise ValueError("No telemetry available")

    monkeypatch.setattr(check_module, "collect_device_observation", denied)
    result = runner.invoke(app, ["check", "--json"])
    assert result.exit_code == 2
    assert "No telemetry" in result.output
