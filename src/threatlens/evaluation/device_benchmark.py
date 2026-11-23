"""Reproducible held-out synthetic evaluation of the deployed source-consensus pipeline.

Labels describe simulated intent. They are not evidence of real compromises.
The hard benign backup and stealth cases intentionally expose limitations.
"""

import random
from copy import deepcopy
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any

from threatlens.detection.device import ALGORITHM_VERSION, assess_observation
from threatlens.evaluation.benchmark import calculate_metrics
from threatlens.schema.device import DeviceObservation

PROFILES = {
    "system": {
        "system": {"cpu_percent": 20, "process_count": 100},
        "network": {"connection_count": 30, "bytes_out": 10000},
        "process": {"total_processes": 100, "high_cpu_process_count": 2},
    },
    "router": {
        "system": {"cpu_percent": 20, "memory_percent": 40},
        "network": {"bytes_out": 10000, "packets_out": 100},
        "routing": {"route_count": 100, "route_changes": 2},
    },
    "firewall": {
        "network": {"bytes_out": 10000, "connection_count": 30},
        "firewall": {"active_sessions": 100, "denied_connections": 5},
    },
    "network": {"network": {"bytes_out": 10000, "unique_remote_addresses": 20}},
}


def make_observation(device_type: str, n: int, sources: dict) -> DeviceObservation:
    timestamp = (datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=n)).isoformat()
    return DeviceObservation(
        f"synthetic-{device_type}", device_type, timestamp, 60.0, deepcopy(sources), {}
    )


def training_observations(device_type: str, seed: int = 42) -> list[DeviceObservation]:
    rng = random.Random(seed)
    result = []
    for n in range(60):
        sources = {
            source: {
                name: max(0, rng.gauss(value, max(0.2, value * 0.05)))
                for name, value in features.items()
            }
            for source, features in PROFILES[device_type].items()
        }
        result.append(make_observation(device_type, n, sources))
    return result


def scenarios(device_type: str) -> list[dict]:
    normal = deepcopy(PROFILES[device_type])
    network_spike = deepcopy(normal)
    network_spike["network"] = {k: v * 10 for k, v in normal["network"].items()}
    multisource = deepcopy(network_spike)
    for source, features in multisource.items():
        if source != "network":
            multisource[source] = {
                k: min(95, v * 4) if k.endswith("percent") else v * 4 for k, v in features.items()
            }
    benign_jitter = {s: {k: v * 1.03 for k, v in f.items()} for s, f in normal.items()}
    # Fresh scenarios; none are included in model fitting.
    return [
        {"name": "normal", "label": False, "windows": [normal]},
        {"name": "benign_jitter", "label": False, "windows": [benign_jitter]},
        {"name": "transient_transfer", "label": False, "windows": [network_spike]},
        {"name": "normal_after_transfer", "label": False, "windows": [network_spike, normal]},
        {
            "name": "sustained_exfiltration_simulation",
            "label": True,
            "windows": [network_spike, network_spike],
        },
        {
            "name": "multisource_compromise_simulation",
            "label": True,
            "windows": [multisource, multisource],
        },
        {
            "name": "authorized_backup_hard_negative",
            "label": False,
            "windows": [multisource, multisource],
        },
        {"name": "stealth_attack_hard_positive", "label": True, "windows": [normal, normal]},
    ]


def run_device_benchmark(seed: int = 42) -> dict[str, Any]:
    results = []
    for device_type in PROFILES:
        baseline = [row.to_dict() for row in training_observations(device_type, seed)]
        for scenario in scenarios(device_type):
            previous, streaks, outputs = baseline[-1], {}, []
            for n, sources in enumerate(scenario["windows"], 60):
                observation = make_observation(device_type, n, sources)
                output = assess_observation(observation, baseline, previous, streaks)
                outputs.append(output)
                previous, streaks = observation.to_dict(), output["streaks"]
            results.append(
                {
                    "device_type": device_type,
                    "name": scenario["name"],
                    "expected_anomaly": scenario["label"],
                    "predicted_anomaly": any(r["is_suspicious"] for r in outputs),
                    "model_only": any(
                        d["model"]["is_anomaly"] for r in outputs for d in r["sources"].values()
                    ),
                    "robust_only": any(
                        d["behavioral"]["is_anomaly"]
                        for r in outputs
                        for d in r["sources"].values()
                    ),
                    "alert_window": next(
                        (n + 1 for n, r in enumerate(outputs) if r["is_suspicious"]), None
                    ),
                    "final_status": outputs[-1]["status"],
                }
            )

    def metrics(rows, key="predicted_anomaly"):
        return asdict(
            calculate_metrics([r["expected_anomaly"] for r in rows], [r[key] for r in rows])
        )

    return {
        "evaluation_type": "held-out synthetic full pipeline; not real attack validation",
        "algorithm_version": ALGORITHM_VERSION,
        "seed": seed,
        "baseline_size": 60,
        "scenario_count": len(results),
        "metrics": metrics(results),
        "by_device": {
            device: metrics([r for r in results if r["device_type"] == device])
            for device in PROFILES
        },
        "ablations": {
            "model_only": metrics(results, "model_only"),
            "robust_only": metrics(results, "robust_only"),
        },
        "scenarios": results,
    }
