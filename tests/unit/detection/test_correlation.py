import pytest

from threatlens.detection.correlation import EventCorrelator


def test_correlates_multiple_triggered_signals():
    correlator = EventCorrelator(minimum_signals=2)

    result = correlator.correlate(
        {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": False,
        }
    )

    assert result["is_correlated"] is True
    assert result["signal_count"] == 2
    assert result["triggered_signals"] == [
        "isolation_forest",
        "temporal_anomaly",
    ]


def test_single_signal_is_not_correlated():
    correlator = EventCorrelator(minimum_signals=2)

    result = correlator.correlate(
        {
            "isolation_forest": True,
            "temporal_anomaly": False,
            "network_anomaly": False,
        }
    )

    assert result["is_correlated"] is False
    assert result["signal_count"] == 1
    assert result["triggered_signals"] == [
        "isolation_forest",
    ]


def test_no_signals_are_not_correlated():
    correlator = EventCorrelator(minimum_signals=2)

    result = correlator.correlate(
        {
            "isolation_forest": False,
            "temporal_anomaly": False,
            "network_anomaly": False,
        }
    )

    assert result["is_correlated"] is False
    assert result["signal_count"] == 0
    assert result["triggered_signals"] == []


def test_custom_signal_threshold():
    correlator = EventCorrelator(minimum_signals=3)

    result = correlator.correlate(
        {
            "isolation_forest": True,
            "temporal_anomaly": True,
            "network_anomaly": True,
        }
    )

    assert result["is_correlated"] is True
    assert result["signal_count"] == 3


def test_invalid_signal_threshold():
    with pytest.raises(ValueError):
        EventCorrelator(minimum_signals=0)
