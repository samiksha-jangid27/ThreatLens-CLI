"""Tests must never read or overwrite the developer's real monitoring state."""

import pytest


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch, tmp_path):
    monkeypatch.setenv("THREATLENS_DATA_DIR", str(tmp_path / "state"))
