from threatlens.explainability.explainer import (
    ThreatExplainer,
)


def test_explainer_reports_isolation_forest():
    explainer = ThreatExplainer()

    result = explainer.explain(
        {
            "signals": {
                "isolation_forest": True,
            },
            "model": {
                "anomaly_score": -0.25,
            },
            "risk": {
                "risk_score": 40.0,
                "severity": "MEDIUM",
            },
        }
    )

    assert result["evidence_count"] == 1

    assert (
        result["evidence"][0]["signal"]
        == "isolation_forest"
    )

    assert (
        result["evidence"][0]["details"][
            "anomaly_score"
        ]
        == -0.25
    )


def test_explainer_reports_multiple_signals():
    explainer = ThreatExplainer()

    result = explainer.explain(
        {
            "signals": {
                "isolation_forest": True,
                "temporal_anomaly": True,
                "behavioral_deviation": True,
                "network_anomaly": True,
                "process_anomaly": True,
            },
            "model": {
                "anomaly_score": -0.4,
            },
            "temporal": {
                "signal_count": 3,
                "triggered_signals": {
                    "cpu_percent": 60.0,
                },
            },
            "behavioral": {
                "anomalous_features": [
                    "cpu_percent",
                    "process_count",
                ],
            },
            "network": {
                "behavioral": {
                    "anomalous_features": [
                        "connection_count",
                    ],
                },
            },
            "process": {
                "behavioral": {
                    "anomalous_features": [
                        "total_processes",
                    ],
                },
            },
            "risk": {
                "risk_score": 90.0,
                "severity": "CRITICAL",
            },
        }
    )

    assert result["evidence_count"] == 5

    assert result["risk_score"] == 90.0

    assert result["severity"] == "CRITICAL"

    assert (
        "5 behavioral signal(s)"
        in result["summary"]
    )


def test_explainer_reports_no_anomaly():
    explainer = ThreatExplainer()

    result = explainer.explain(
        {
            "signals": {},
            "risk": {
                "risk_score": 0.0,
                "severity": "LOW",
            },
        }
    )

    assert result["evidence_count"] == 0

    assert (
        result["evidence"] == []
    )

    assert (
        result["summary"]
        == "No anomalous behavioral evidence "
        "was identified."
    )


def test_explainer_reports_network_evidence():
    explainer = ThreatExplainer()

    result = explainer.explain(
        {
            "signals": {
                "network_anomaly": True,
            },
            "network": {
                "behavioral": {
                    "anomalous_features": [
                        "connection_count",
                        "unique_remote_addresses",
                    ],
                },
            },
            "risk": {
                "risk_score": 20.0,
                "severity": "LOW",
            },
        }
    )

    assert result["evidence_count"] == 1

    assert (
        result["evidence"][0]["signal"]
        == "network_anomaly"
    )

    assert (
        result["evidence"][0]["details"][
            "anomalous_features"
        ]
        == [
            "connection_count",
            "unique_remote_addresses",
        ]
    )


def test_explainer_reports_process_evidence():
    explainer = ThreatExplainer()

    result = explainer.explain(
        {
            "signals": {
                "process_anomaly": True,
            },
            "process": {
                "behavioral": {
                    "anomalous_features": [
                        "total_processes",
                        "root_process_count",
                    ],
                },
            },
            "risk": {
                "risk_score": 15.0,
                "severity": "LOW",
            },
        }
    )

    assert result["evidence_count"] == 1

    assert (
        result["evidence"][0]["signal"]
        == "process_anomaly"
    )