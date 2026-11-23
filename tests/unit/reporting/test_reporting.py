import json

from threatlens.reporting.html import (
    generate_html_report,
)
from threatlens.reporting.json import (
    generate_json_report,
)


def sample_incidents():
    return [
        {
            "id": 1,
            "timestamp": (
                "2026-09-20T18:00:00+05:30"
            ),
            "risk_score": 80.0,
            "severity": "CRITICAL",
            "is_suspicious": True,
            "signals": {
                "isolation_forest": True,
                "temporal_anomaly": True,
                "network_anomaly": False,
                "process_anomaly": True,
            },
        },
        {
            "id": 2,
            "timestamp": (
                "2026-09-20T18:05:00+05:30"
            ),
            "risk_score": 0.0,
            "severity": "LOW",
            "is_suspicious": False,
            "signals": {},
        },
    ]


def test_json_report():
    content = generate_json_report(
        sample_incidents()
    )

    payload = json.loads(content)

    assert (
        payload["summary"]["total_incidents"]
        == 2
    )

    assert (
        payload["summary"][
            "suspicious_incidents"
        ]
        == 1
    )

    assert (
        payload["incidents"][0]["risk_score"]
        == 80.0
    )


def test_json_report_empty():
    content = generate_json_report([])

    payload = json.loads(content)

    assert (
        payload["summary"]["total_incidents"]
        == 0
    )

    assert (
        payload["summary"][
            "suspicious_incidents"
        ]
        == 0
    )


def test_html_report():
    content = generate_html_report(
        sample_incidents()
    )

    assert (
        "<title>ThreatLens Security Report</title>"
        in content
    )

    assert "CRITICAL" in content

    assert "isolation_forest" in content

    assert "Suspicious Incidents" in content


def test_html_report_empty():
    content = generate_html_report([])

    assert (
        "ThreatLens Security Report"
        in content
    )

    assert "Total Incidents" in content


def test_html_includes_escaped_feature_evidence():
    from threatlens.reporting.html import generate_html_report
    report = generate_html_report([{
        "id": 1, "timestamp": "2026-01-01", "risk_score": 50, "severity": "MEDIUM",
        "is_suspicious": True, "signals": {"network": True},
        "explanation": {"description": "<script>alert(1)</script>", "current": 999},
    }])
    assert "&lt;script&gt;" in report
    assert "<script>" not in report
    assert "999" in report
    assert "Content-Security-Policy" in report
