from threatlens.evaluation.benchmark import (
    calculate_metrics,
    create_benchmark_scenarios,
    run_benchmark,
)


def test_create_benchmark_scenarios():
    scenarios = create_benchmark_scenarios()

    assert len(scenarios) == 10

    assert (
        scenarios[0].expected_anomaly
        is False
    )

    assert (
        scenarios[-1].expected_anomaly
        is True
    )


def test_calculate_metrics():
    expected = [
        True,
        True,
        False,
        False,
    ]

    predicted = [
        True,
        False,
        False,
        True,
    ]

    metrics = calculate_metrics(
        expected,
        predicted,
    )

    assert metrics.true_positive == 1
    assert metrics.true_negative == 1
    assert metrics.false_positive == 1
    assert metrics.false_negative == 1

    assert metrics.accuracy == 0.5
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1 == 0.5
    assert metrics.false_positive_rate == 0.5
    assert metrics.detection_rate == 0.5


def test_benchmark_runs():
    result = run_benchmark()

    assert (
        result["baseline_size"]
        == 5
    )

    assert (
        result["scenario_count"]
        == 10
    )

    metrics = result["metrics"]

    assert (
        metrics["true_positive"]
        >= 1
    )

    assert (
        metrics["false_positive"]
        >= 0
    )

    assert (
        0.0
        <= metrics["accuracy"]
        <= 1.0
    )

    assert (
        0.0
        <= metrics["precision"]
        <= 1.0
    )

    assert (
        0.0
        <= metrics["recall"]
        <= 1.0
    )

    assert (
        0.0
        <= metrics["f1"]
        <= 1.0
    )

    assert (
        0.0
        <= metrics["false_positive_rate"]
        <= 1.0
    )


def test_benchmark_reports_scenario_results():
    result = run_benchmark()

    assert len(
        result["scenarios"]
    ) == 10

    for scenario in result["scenarios"]:
        assert "name" in scenario
        assert "expected_anomaly" in scenario
        assert "predicted_anomaly" in scenario
        assert "correct" in scenario
        assert "anomalous_features" in scenario
