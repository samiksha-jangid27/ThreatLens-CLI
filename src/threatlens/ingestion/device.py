"""Bounded strict JSON imports. No pickle, eval, subprocess, or network access."""

import json
from pathlib import Path

from threatlens.schema.device import DeviceObservation, parse_document

MAX_INPUT_BYTES = 10 * 1024 * 1024


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def load_document(path: Path) -> list[DeviceObservation]:
    with path.open("rb") as stream:
        content = stream.read(MAX_INPUT_BYTES + 1)
    if len(content) > MAX_INPUT_BYTES:
        raise ValueError("Telemetry input exceeds 10 MiB")
    return parse_document(json.loads(content, object_pairs_hook=_unique_pairs))
