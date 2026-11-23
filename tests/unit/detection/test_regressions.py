import pytest

from threatlens.detection.baseline import BehavioralBaseline
from threatlens.detection.behavioral import BehavioralDeviationDetector
from threatlens.detection.risk import RiskScorer
from threatlens.models.isolation_forest import IsolationForestDetector


def test_uptime_drift_does_not_change_model_decision():
    detector = IsolationForestDetector()
    detector.fit([{"cpu_percent": 20, "uptime_seconds": n} for n in range(30)])
    assert detector.predict({"cpu_percent": 20, "uptime_seconds": 1}) == detector.predict(
        {"cpu_percent": 20, "uptime_seconds": 1_000_000}
    )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True])
def test_model_rejects_invalid_numbers(value):
    with pytest.raises(ValueError, match="finite"):
        IsolationForestDetector().fit([{"cpu": value}])


def test_schema_drift_is_explicit():
    with pytest.raises(ValueError, match="identical"):
        IsolationForestDetector().fit([{"cpu": 20}, {"memory": 20}])
    with pytest.raises(ValueError, match="missing is not zero"):
        BehavioralDeviationDetector().analyze({"cpu": 20}, [{"memory": 20}])


def test_tiny_nonzero_variance_needs_meaningful_change():
    result = BehavioralDeviationDetector().analyze(
        {"cpu": 20.001}, [{"cpu": 20 + n * 0.000001} for n in range(30)]
    )
    assert not result["is_anomaly"]


def test_late_feature_mean_uses_own_count():
    baseline = BehavioralBaseline()
    baseline.update({"cpu": 1})
    baseline.update({"cpu": 2, "new": 10})
    baseline.update({"cpu": 3, "new": 20})
    assert baseline.means["new"] == 15


def test_behavioral_signal_contributes_risk_and_invalid_weights_fail():
    assert RiskScorer().score({"behavioral_deviation": True})["risk_score"] > 0
    with pytest.raises(ValueError):
        RiskScorer({"cpu": -5})
