import json
from copy import deepcopy

import pytest

from threatlens.ingestion.device import load_document
from threatlens.schema.device import parse_document


def document(device_type="router"):
    return {
        "schema_version": 1,
        "device_id": "lab-router",
        "device_type": device_type,
        "observations": [
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "window_seconds": 60,
                "sources": {"network": {"bytes_out": 1024}},
                "unavailable": {},
            }
        ],
    }


@pytest.mark.parametrize("device_type", ["system", "router", "firewall", "network"])
def test_all_device_types_use_same_contract(device_type):
    assert parse_document(document(device_type))[0].sources["network"]["bytes_out"] == 1024.0


@pytest.mark.parametrize("value", [True, "100", -1, float("nan"), float("inf")])
def test_bad_metric_rejected(value):
    data = document()
    data["observations"][0]["sources"]["network"]["bytes_out"] = value
    with pytest.raises(ValueError):
        parse_document(data)


def test_reordered_or_naive_time_rejected():
    data = document()
    data["observations"].append(deepcopy(data["observations"][0]))
    with pytest.raises(ValueError, match="increasing"):
        parse_document(data)
    data["observations"] = data["observations"][:1]
    data["observations"][0]["timestamp"] = "2026-01-01"
    with pytest.raises(ValueError, match="timezone"):
        parse_document(data)


def test_unknown_source_rejected():
    data = document()
    data["observations"][0]["sources"]["firewall"] = {"active_sessions": 3}
    with pytest.raises(ValueError, match="unsupported"):
        parse_document(data)


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version": 1,"schema_version": 2}')
    with pytest.raises(ValueError, match="Duplicate"):
        load_document(path)


def test_round_trip(tmp_path):
    path = tmp_path / "router.json"
    path.write_text(json.dumps(document()))
    assert load_document(path)[0].device_type == "router"
