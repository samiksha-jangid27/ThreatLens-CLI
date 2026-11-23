from datetime import UTC, datetime, timedelta

import pytest

from threatlens.detection.device import DeviceDetectionService
from threatlens.schema.device import DeviceObservation
from threatlens.storage.database import ThreatLensDatabase
from threatlens.storage.repositories import IncidentRepository


def observation(n, network=100, cpu=20, device_id="router-1", sources=None):
    return DeviceObservation(
        device_id,
        "router",
        (datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=n)).isoformat(),
        60,
        sources or {"system": {"cpu_percent": cpu}, "network": {"bytes_out": network}},
        {},
    )


@pytest.fixture
def service(tmp_path):
    return DeviceDetectionService(IncidentRepository(ThreatLensDatabase(tmp_path / "state.db")))


def train(service):
    service.learn([observation(n, 100 + n % 3, 20 + n % 3) for n in range(30)])


def test_untrained_scan_does_not_claim_clean_or_learn(service):
    assert service.scan([observation(0)])[0]["status"] == "INSUFFICIENT_BASELINE"
    assert service.status() == []


def test_two_sources_create_incident_with_evidence_and_frozen_baseline(service):
    train(service)
    result = service.scan([observation(30, 10000, 95)])[0]
    assert result["is_suspicious"]
    record = service.repository.get(result["incident_id"])
    assert record["features"] == result["features"]
    assert record["explanation"]["evidence"]
    assert service.status()[0]["baseline_size"] == 30


def test_transient_is_review_persistent_is_suspicious(service):
    train(service)
    assert service.scan([observation(30, 10000)])[0]["status"] == "REVIEW"
    assert service.scan([observation(31, 10000)])[0]["is_suspicious"]


def test_gap_resets_persistence(service):
    train(service)
    service.scan([observation(30, 10000)])
    assert not service.scan([observation(80, 10000)])[0]["is_suspicious"]


def test_replay_and_schema_drift_roll_back(service):
    train(service)
    with pytest.raises(ValueError, match="out-of-order"):
        service.scan([observation(30, 10000, 95), observation(29)])
    assert service.repository.list_all() == []
    assert service.status()[0]["last_observation"] == observation(29).timestamp
    with pytest.raises(ValueError, match="feature names"):
        service.scan([observation(30, sources={"system": {"memory_percent": 40}})])


def test_device_baselines_are_isolated(service):
    train(service)
    assert (
        service.scan([observation(30, device_id="router-2")])[0]["status"]
        == "INSUFFICIENT_BASELINE"
    )


def test_missing_source_is_degraded_not_zero(service):
    train(service)
    result = service.scan([observation(30, sources={"system": {"cpu_percent": 20}})])[0]
    assert result["coverage"]["degraded"]
    assert result["coverage"]["missing_sources"] == ["network"]
    assert "network" not in result["sources"]


def test_relearning_requires_explicit_replace_for_profile_change(service):
    train(service)
    with pytest.raises(ValueError, match="schema"):
        service.learn([observation(30, sources={"system": {"cpu_percent": 20}})])
    result = service.learn([observation(30, sources={"system": {"cpu_percent": 20}})], replace=True)
    assert not result["ready"]
