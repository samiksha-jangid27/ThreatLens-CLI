from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.repositories import IncidentRepository


def sample_detection_result():
    return {
        "timestamp": "2026-09-20T12:00:00+00:00",
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
            "risk_score": 80.0,
            "severity": "CRITICAL",
            "contributions": {
                "isolation_forest": 40.0,
                "temporal_anomaly": 25.0,
                "process_anomaly": 15.0,
            },
            "triggered_signals": [
                "isolation_forest",
                "temporal_anomaly",
                "process_anomaly",
            ],
        },
        "is_suspicious": True,
    }


def test_database_initializes(tmp_path):
    database = ThreatLensDatabase(
        tmp_path / "threatlens.db"
    )

    database.initialize()

    with database.connect() as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'incidents'
            """
        ).fetchall()

    assert len(tables) == 1


def test_create_incident(tmp_path):
    database = ThreatLensDatabase(
        tmp_path / "threatlens.db"
    )

    repository = IncidentRepository(database)

    incident_id = repository.create(
        sample_detection_result()
    )

    assert incident_id == 1


def test_get_incident(tmp_path):
    database = ThreatLensDatabase(
        tmp_path / "threatlens.db"
    )

    repository = IncidentRepository(database)

    incident_id = repository.create(
        sample_detection_result()
    )

    incident = repository.get(incident_id)

    assert incident is not None
    assert incident["id"] == incident_id
    assert incident["risk_score"] == 80.0
    assert incident["severity"] == "CRITICAL"
    assert incident["is_suspicious"] is True
    assert incident["signals"]["isolation_forest"] is True


def test_get_missing_incident(tmp_path):
    database = ThreatLensDatabase(
        tmp_path / "threatlens.db"
    )

    repository = IncidentRepository(database)

    assert repository.get(999) is None


def test_list_incidents(tmp_path):
    database = ThreatLensDatabase(
        tmp_path / "threatlens.db"
    )

    repository = IncidentRepository(database)

    repository.create(
        sample_detection_result()
    )

    second_result = sample_detection_result()
    second_result["risk"]["risk_score"] = 40.0
    second_result["risk"]["severity"] = "MEDIUM"
    second_result["is_suspicious"] = False

    repository.create(second_result)

    incidents = repository.list_all()

    assert len(incidents) == 2

    # Newest incident first.
    assert incidents[0]["id"] == 2
    assert incidents[1]["id"] == 1
    assert incidents[0]["risk_score"] == 40.0
    assert incidents[1]["risk_score"] == 80.0