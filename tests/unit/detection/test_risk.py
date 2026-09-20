import pytest

from threatlens.detection.risk import RiskScorer


def test_calculates_risk_from_triggered_signals():
    scorer = RiskScorer()

    result = scorer.score(
        {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": False,
            "process_anomaly": True,
        }
    )

    assert result["risk_score"] == 80.0
    assert result["severity"] == "CRITICAL"
    assert result["triggered_signals"] == [
        "isolation_forest",
        "temporal_anomaly",
        "process_anomaly",
    ]


def test_no_signals_produce_low_risk():
    scorer = RiskScorer()

    result = scorer.score(
        {
            "isolation_forest": False,
            "temporal_anomaly": False,
            "network_anomaly": False,
            "process_anomaly": False,
        }
    )

    assert result["risk_score"] == 0.0
    assert result["severity"] == "LOW"
    assert result["triggered_signals"] == []


def test_unknown_signal_has_no_weight():
    scorer = RiskScorer()

    result = scorer.score(
        {
            "unknown_signal": True,
        }
    )

    assert result["risk_score"] == 0.0
    assert result["severity"] == "LOW"


def test_score_is_capped_at_100():
    scorer = RiskScorer(
        weights={
            "signal_a": 80,
            "signal_b": 70,
        }
    )

    result = scorer.score(
        {
            "signal_a": True,
            "signal_b": True,
        }
    )

    assert result["risk_score"] == 100.0


@pytest.mark.parametrize(
    ("score", "severity"),
    [
        (0, "LOW"),
        (29, "LOW"),
        (30, "MEDIUM"),
        (59, "MEDIUM"),
        (60, "HIGH"),
        (79, "HIGH"),
        (80, "CRITICAL"),
        (100, "CRITICAL"),
    ],
)
def test_severity_thresholds(score, severity):
    scorer = RiskScorer()

    assert scorer._severity(score) == severity
