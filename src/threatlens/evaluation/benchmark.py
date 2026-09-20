from dataclasses import dataclass
from typing import Any

from threatlens.detection.behavioral import (
    BehavioralDeviationDetector,
)


@dataclass(frozen=True)
class BenchmarkScenario:
    """
    One labeled behavioral detection scenario.
    """

    name: str
    features: dict[str, float]
    expected_anomaly: bool


@dataclass(frozen=True)
class BenchmarkMetrics:
    """
    Standard binary classification metrics.
    """

    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    false_positive_rate: float
    detection_rate: float


SYSTEM_BASELINE = [
    {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.0,
        "process_count": 100.0,
        "disk_percent": 50.0,
    },
    {
        "cpu_percent": 21.0,
        "memory_percent": 41.0,
        "load_average_1m": 1.1,
        "process_count": 102.0,
        "disk_percent": 50.0,
    },
    {
        "cpu_percent": 19.0,
        "memory_percent": 39.0,
        "load_average_1m": 0.9,
        "process_count": 99.0,
        "disk_percent": 49.0,
    },
    {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.0,
        "process_count": 101.0,
        "disk_percent": 50.0,
    },
    {
        "cpu_percent": 21.0,
        "memory_percent": 40.0,
        "load_average_1m": 1.1,
        "process_count": 100.0,
        "disk_percent": 51.0,
    },
]


def create_benchmark_scenarios() -> list[BenchmarkScenario]:
    """
    Create deterministic normal and anomalous scenarios.
    """

    return [
        BenchmarkScenario(
            name="normal_1",
            features={
                "cpu_percent": 20.5,
                "memory_percent": 40.5,
                "load_average_1m": 1.0,
                "process_count": 101.0,
                "disk_percent": 50.0,
            },
            expected_anomaly=False,
        ),
        BenchmarkScenario(
            name="normal_2",
            features={
                "cpu_percent": 22.0,
                "memory_percent": 42.0,
                "load_average_1m": 1.2,
                "process_count": 103.0,
                "disk_percent": 51.0,
            },
            expected_anomaly=False,
        ),
        BenchmarkScenario(
            name="normal_3",
            features={
                "cpu_percent": 18.5,
                "memory_percent": 38.5,
                "load_average_1m": 0.8,
                "process_count": 98.0,
                "disk_percent": 49.0,
            },
            expected_anomaly=False,
        ),
        BenchmarkScenario(
            name="normal_4",
            features={
                "cpu_percent": 21.0,
                "memory_percent": 39.5,
                "load_average_1m": 1.05,
                "process_count": 102.0,
                "disk_percent": 50.5,
            },
            expected_anomaly=False,
        ),
        BenchmarkScenario(
            name="normal_5",
            features={
                "cpu_percent": 19.5,
                "memory_percent": 41.0,
                "load_average_1m": 0.95,
                "process_count": 100.0,
                "disk_percent": 50.0,
            },
            expected_anomaly=False,
        ),
        BenchmarkScenario(
            name="cpu_spike",
            features={
                "cpu_percent": 85.0,
                "memory_percent": 42.0,
                "load_average_1m": 1.5,
                "process_count": 105.0,
                "disk_percent": 50.0,
            },
            expected_anomaly=True,
        ),
        BenchmarkScenario(
            name="memory_spike",
            features={
                "cpu_percent": 22.0,
                "memory_percent": 90.0,
                "load_average_1m": 1.2,
                "process_count": 105.0,
                "disk_percent": 51.0,
            },
            expected_anomaly=True,
        ),
        BenchmarkScenario(
            name="process_spike",
            features={
                "cpu_percent": 25.0,
                "memory_percent": 45.0,
                "load_average_1m": 1.5,
                "process_count": 220.0,
                "disk_percent": 51.0,
            },
            expected_anomaly=True,
        ),
        BenchmarkScenario(
            name="load_spike",
            features={
                "cpu_percent": 35.0,
                "memory_percent": 48.0,
                "load_average_1m": 8.0,
                "process_count": 110.0,
                "disk_percent": 52.0,
            },
            expected_anomaly=True,
        ),
        BenchmarkScenario(
            name="multi_signal_spike",
            features={
                "cpu_percent": 90.0,
                "memory_percent": 88.0,
                "load_average_1m": 9.0,
                "process_count": 240.0,
                "disk_percent": 82.0,
            },
            expected_anomaly=True,
        ),
    ]


def calculate_metrics(
    expected: list[bool],
    predicted: list[bool],
) -> BenchmarkMetrics:
    """
    Calculate binary classification metrics.
    """

    true_positive = sum(
        expected_value and predicted_value
        for expected_value, predicted_value
        in zip(expected, predicted)
    )

    true_negative = sum(
        not expected_value and not predicted_value
        for expected_value, predicted_value
        in zip(expected, predicted)
    )

    false_positive = sum(
        not expected_value and predicted_value
        for expected_value, predicted_value
        in zip(expected, predicted)
    )

    false_negative = sum(
        expected_value and not predicted_value
        for expected_value, predicted_value
        in zip(expected, predicted)
    )

    total = len(expected)

    accuracy = (
        (true_positive + true_negative) / total
        if total
        else 0.0
    )

    precision = (
        true_positive
        / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0.0
    )

    recall = (
        true_positive
        / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    normal_count = (
        true_negative + false_positive
    )

    false_positive_rate = (
        false_positive / normal_count
        if normal_count
        else 0.0
    )

    detection_rate = recall

    return BenchmarkMetrics(
        true_positive=true_positive,
        true_negative=true_negative,
        false_positive=false_positive,
        false_negative=false_negative,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        false_positive_rate=false_positive_rate,
        detection_rate=detection_rate,
    )


def run_benchmark(
    baseline: list[dict[str, float]] | None = None,
    scenarios: list[BenchmarkScenario] | None = None,
) -> dict[str, Any]:
    """
    Run the behavioral detection benchmark.
    """

    detector = BehavioralDeviationDetector(
        threshold=3.0,
    )

    baseline_data = (
        baseline
        if baseline is not None
        else SYSTEM_BASELINE
    )

    benchmark_scenarios = (
        scenarios
        if scenarios is not None
        else create_benchmark_scenarios()
    )

    expected: list[bool] = []
    predicted: list[bool] = []

    scenario_results = []

    for scenario in benchmark_scenarios:
        result = detector.analyze(
            scenario.features,
            baseline_data,
        )

        prediction = bool(
            result["is_anomaly"]
        )

        expected.append(
            scenario.expected_anomaly
        )

        predicted.append(
            prediction
        )

        scenario_results.append(
            {
                "name": scenario.name,
                "expected_anomaly": (
                    scenario.expected_anomaly
                ),
                "predicted_anomaly": prediction,
                "correct": (
                    scenario.expected_anomaly
                    == prediction
                ),
                "anomalous_features": result[
                    "anomalous_features"
                ],
            }
        )

    metrics = calculate_metrics(
        expected,
        predicted,
    )

    return {
        "baseline_size": len(
            baseline_data
        ),
        "scenario_count": len(
            benchmark_scenarios
        ),
        "metrics": {
            "true_positive": (
                metrics.true_positive
            ),
            "true_negative": (
                metrics.true_negative
            ),
            "false_positive": (
                metrics.false_positive
            ),
            "false_negative": (
                metrics.false_negative
            ),
            "accuracy": metrics.accuracy,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1": metrics.f1,
            "false_positive_rate": (
                metrics.false_positive_rate
            ),
            "detection_rate": (
                metrics.detection_rate
            ),
        },
        "scenarios": scenario_results,
    }
