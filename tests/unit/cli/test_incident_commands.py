import json

from typer.testing import CliRunner

from threatlens.cli.app import app
from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.repositories import IncidentRepository


runner = CliRunner()


def test_incidents_command_is_registered():
    result = runner.invoke(
        app,
        ["incidents"],
    )

    assert result.exit_code == 0


def test_investigate_command_is_registered():
    result = runner.invoke(
        app,
        ["investigate", "999999"],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_explain_command_is_registered():
    result = runner.invoke(
        app,
        ["explain", "999999"],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_incidents_json_output(
    monkeypatch,
    tmp_path,
):
    database_path = tmp_path / "threatlens.db"

    repository = IncidentRepository(
        ThreatLensDatabase(database_path)
    )

    detection_result = {
        "timestamp": (
            "2026-09-20T18:00:00+05:30"
        ),
        "signals": {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": False,
            "process_anomaly": True,
        },
        "correlation": {
            "is_correlated": True,
            "signal_count": 3,
            "triggered_signals": [
                "isolation_forest",
                "temporal_anomaly",
                "process_anomaly",
            ],
        },
        "risk": {
            "risk_score": 80,
            "severity": "CRITICAL",
            "contributions": {
                "isolation_forest": 40,
                "temporal_anomaly": 25,
                "process_anomaly": 15,
            },
            "triggered_signals": [
                "isolation_forest",
                "temporal_anomaly",
                "process_anomaly",
            ],
        },
        "is_suspicious": True,
    }

    incident_id = repository.create(
        detection_result
    )

    from threatlens.cli.commands import (
        incidents as incidents_module,
    )

    monkeypatch.setattr(
        incidents_module,
        "_get_repository",
        lambda: repository,
    )

    result = runner.invoke(
        app,
        ["incidents", "--json"],
    )

    assert result.exit_code == 0

    payload = json.loads(
        result.stdout
    )

    assert payload["count"] == 1

    assert (
        payload["incidents"][0]["id"]
        == incident_id
    )

    assert (
        payload["incidents"][0]["risk_score"]
        == 80.0
    )

    assert (
        payload["incidents"][0]["severity"]
        == "CRITICAL"
    )


def test_explain_json_output(
    monkeypatch,
    tmp_path,
):
    database_path = (
        tmp_path / "threatlens.db"
    )

    repository = IncidentRepository(
        ThreatLensDatabase(database_path)
    )

    detection_result = {
        "timestamp": (
            "2026-09-20T18:00:00+05:30"
        ),
        "signals": {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": False,
            "process_anomaly": False,
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
            "risk_score": 65,
            "severity": "HIGH",
            "contributions": {
                "isolation_forest": 40,
                "temporal_anomaly": 25,
            },
            "triggered_signals": [
                "isolation_forest",
                "temporal_anomaly",
            ],
        },
        "is_suspicious": True,
    }

    incident_id = repository.create(
        detection_result
    )

    from threatlens.cli.commands import (
        explain as explain_module,
    )

    monkeypatch.setattr(
        explain_module,
        "_get_repository",
        lambda: repository,
    )

    result = runner.invoke(
        app,
        [
            "explain",
            str(incident_id),
            "--json",
        ],
    )

    assert result.exit_code == 0

    payload = json.loads(
        result.stdout
    )

    assert (
        payload["incident_id"]
        == incident_id
    )

    assert (
        payload["risk_score"]
        == 65.0
    )

    assert (
        payload["severity"]
        == "HIGH"
    )

    assert (
        payload["evidence_count"]
        == 2
    )


def test_investigate_shows_evidence(
    monkeypatch,
    tmp_path,
):
    database_path = (
        tmp_path / "threatlens.db"
    )

    repository = IncidentRepository(
        ThreatLensDatabase(database_path)
    )

    detection_result = {
        "timestamp": (
            "2026-09-20T18:00:00+05:30"
        ),
        "signals": {
            "network_anomaly": True,
            "process_anomaly": True,
        },
        "correlation": {
            "is_correlated": True,
            "signal_count": 2,
            "triggered_signals": [
                "network_anomaly",
                "process_anomaly",
            ],
        },
        "risk": {
            "risk_score": 35,
            "severity": "MEDIUM",
            "contributions": {
                "network_anomaly": 20,
                "process_anomaly": 15,
            },
            "triggered_signals": [
                "network_anomaly",
                "process_anomaly",
            ],
        },
        "is_suspicious": True,
    }

    incident_id = repository.create(
        detection_result
    )

    from threatlens.cli.commands import (
        investigate as investigate_module,
    )

    monkeypatch.setattr(
        investigate_module,
        "_get_repository",
        lambda: repository,
    )

    result = runner.invoke(
        app,
        [
            "investigate",
            str(incident_id),
        ],
    )

    assert result.exit_code == 0

    assert (
        "behavioral evidence"
        in result.stdout.lower()
    )

    assert (
        "network_anomaly"
        in result.stdout
    )

    assert (
        "process_anomaly"
        in result.stdout
    )