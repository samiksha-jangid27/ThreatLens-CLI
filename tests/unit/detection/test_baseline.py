from threatlens.detection.baseline import BehavioralBaseline


def test_baseline_learns_mean_minimum_and_maximum():
    baseline = BehavioralBaseline()

    baseline.update(
        {
            "cpu_percent": 20.0,
            "memory_percent": 40.0,
        }
    )

    baseline.update(
        {
            "cpu_percent": 60.0,
            "memory_percent": 50.0,
        }
    )

    baseline.update(
        {
            "cpu_percent": 40.0,
            "memory_percent": 30.0,
        }
    )

    summary = baseline.summary()

    assert summary["observations"] == 3

    assert summary["means"]["cpu_percent"] == 40.0
    assert summary["means"]["memory_percent"] == 40.0

    assert summary["minimums"]["cpu_percent"] == 20.0
    assert summary["maximums"]["cpu_percent"] == 60.0

    assert summary["minimums"]["memory_percent"] == 30.0
    assert summary["maximums"]["memory_percent"] == 50.0


def test_empty_baseline():
    baseline = BehavioralBaseline()

    summary = baseline.summary()

    assert summary["observations"] == 0
    assert summary["means"] == {}
    assert summary["minimums"] == {}
    assert summary["maximums"] == {}