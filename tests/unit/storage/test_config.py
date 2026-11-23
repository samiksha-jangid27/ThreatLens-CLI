from pathlib import Path

from threatlens.config import database_path
from threatlens.storage.database import ThreatLensDatabase


def test_commands_share_configured_database(monkeypatch, tmp_path):
    monkeypatch.setenv("THREATLENS_DATA_DIR", str(tmp_path / "private"))
    expected = tmp_path / "private" / "threatlens.db"
    assert database_path() == expected
    ThreatLensDatabase(expected).initialize()
    assert expected.exists()
    if __import__("os").name == "posix":
        assert expected.stat().st_mode & 0o077 == 0


def test_default_location_is_backwards_compatible(monkeypatch):
    monkeypatch.delenv("THREATLENS_DATA_DIR", raising=False)
    assert database_path() == Path.home() / ".threatlens" / "threatlens.db"
