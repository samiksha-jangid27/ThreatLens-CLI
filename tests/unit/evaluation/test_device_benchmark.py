import pytest

from threatlens.evaluation.benchmark import calculate_metrics
from threatlens.evaluation.device_benchmark import run_device_benchmark


def test_full_pipeline_benchmark_reports_hard_cases_and_all_devices():
    result = run_device_benchmark()
    assert result["scenario_count"] == 32
    assert set(result["by_device"]) == {"system", "router", "firewall", "network"}
    assert result["metrics"]["false_positive"] >= 1
    assert result["metrics"]["false_negative"] >= 1
    assert result["metrics"]["true_positive"] >= 1
    assert any(row["alert_window"] == 2 for row in result["scenarios"])
    assert (
        result["ablations"]["robust_only"]["false_positive"] >= result["metrics"]["false_positive"]
    )


def test_metrics_reject_silently_truncated_inputs():
    with pytest.raises(ValueError, match="equal lengths"):
        calculate_metrics([True, False], [True])
