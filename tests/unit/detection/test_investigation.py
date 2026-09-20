from threatlens.detection.investigation import IncidentInvestigator


def make_incident(
    risk_score: float,
    severity: str,
    signals: dict[str, bool],
) -> dict:
    return {
        "id": 1,
        "timestamp": "2026-09-20T12:00:00+00:00",
        "risk_score": risk_score,
        "severity": severity,
        "is_suspicious": risk_score >= 30,
        "signals": signals,
    }


def test_investigates_multi_signal_incident():
    investigator = IncidentInvestigator()

    incident = make_incident(
        80.0,
        "CRITICAL",
        {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": False,
            "process_anomaly": True,
        },
    )

    result = investigator.investigate(incident)

    assert result["incident_id"] == 1
    assert result["status"] == "MULTI_SIGNAL"
    assert result["priority"] == "CRITICAL"
    assert result["risk_score"] == 80.0
    assert result["signal_count"] == 3

    assert result["triggered_signals"] == [
        "isolation_forest",
        "temporal_anomaly",
        "process_anomaly",
    ]


def test_investigates_single_signal_incident():
    investigator = IncidentInvestigator()

    incident = make_incident(
        40.0,
        "MEDIUM",
        {
            "isolation_forest": True,
            "temporal_anomaly": False,
            "network_anomaly": False,
            "process_anomaly": False,
        },
    )

    result = investigator.investigate(incident)

    assert result["status"] == "SINGLE_SIGNAL"
    assert result["priority"] == "MEDIUM"
    assert result["signal_count"] == 1
    assert (
        result["recommendation"]
        == "Collect additional telemetry before escalating."
    )


def test_investigates_incident_without_signals():
    investigator = IncidentInvestigator()

    incident = make_incident(
        0.0,
        "LOW",
        {
            "isolation_forest": False,
            "temporal_anomaly": False,
            "network_anomaly": False,
            "process_anomaly": False,
        },
    )

    result = investigator.investigate(incident)

    assert result["status"] == "NO_ANOMALOUS_SIGNALS"
    assert result["priority"] == "LOW"
    assert result["signal_count"] == 0
    assert result["triggered_signals"] == []
    assert result["recommendation"] == "Continue monitoring."


def test_priority_thresholds():
    investigator = IncidentInvestigator()

    low = make_incident(20.0, "LOW", {})
    medium = make_incident(30.0, "MEDIUM", {})
    high = make_incident(60.0, "HIGH", {})
    critical = make_incident(80.0, "CRITICAL", {})

    assert investigator.investigate(low)["priority"] == "LOW"
    assert investigator.investigate(medium)["priority"] == "MEDIUM"
    assert investigator.investigate(high)["priority"] == "HIGH"
    assert investigator.investigate(critical)["priority"] == "CRITICAL"
