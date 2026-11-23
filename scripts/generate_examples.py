"""Regenerate public synthetic fixtures; no real hosts or attacks are involved."""

import argparse
import json
from copy import deepcopy
from pathlib import Path

from threatlens.evaluation.device_benchmark import PROFILES, make_observation, training_observations


def document(observations):
    first = observations[0]
    return {
        "schema_version": 1,
        "device_id": first.device_id,
        "device_type": first.device_type,
        "observations": [
            {k: v for k, v in row.to_dict().items() if k not in {"device_id", "device_type"}}
            for row in observations
        ],
    }


def generate(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    for kind, profile in PROFILES.items():
        training = training_observations(kind)
        attack = deepcopy(profile)
        attack["network"] = {k: v * 10 for k, v in profile["network"].items()}
        fixtures = {
            "baseline": training,
            "normal": [make_observation(kind, 60, profile)],
            "suspicious": [make_observation(kind, n, attack) for n in (61, 62)],
        }
        for name, observations in fixtures.items():
            (output / f"{kind}-{name}.json").write_text(
                json.dumps(document(observations), indent=2) + "\n", encoding="utf-8"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("examples"))
    generate(parser.parse_args().output)
