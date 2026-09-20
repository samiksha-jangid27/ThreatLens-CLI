import json

import typer
from rich.console import Console
from rich.table import Table

from threatlens.evaluation.benchmark import (
    run_benchmark,
)


console = Console()


def benchmark(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output benchmark results as JSON.",
    ),
) -> None:
    """Run the ThreatLens behavioral detection benchmark."""

    result = run_benchmark()

    if json_output:
        print(
            json.dumps(
                result,
                indent=2,
            )
        )
        return

    metrics = result["metrics"]

    table = Table(
        title="ThreatLens Detection Benchmark"
    )

    table.add_column("Metric")
    table.add_column(
        "Value",
        justify="right",
    )

    table.add_row(
        "Accuracy",
        f'{metrics["accuracy"]:.2%}',
    )

    table.add_row(
        "Precision",
        f'{metrics["precision"]:.2%}',
    )

    table.add_row(
        "Recall",
        f'{metrics["recall"]:.2%}',
    )

    table.add_row(
        "F1 Score",
        f'{metrics["f1"]:.2%}',
    )

    table.add_row(
        "False Positive Rate",
        f'{metrics["false_positive_rate"]:.2%}',
    )

    table.add_row(
        "Detection Rate",
        f'{metrics["detection_rate"]:.2%}',
    )

    console.print(table)

    console.print(
        f"\nScenarios tested: "
        f'{result["scenario_count"]}'
    )

    console.print(
        f'Baseline observations: '
        f'{result["baseline_size"]}'
    )
