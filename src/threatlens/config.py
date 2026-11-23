"""Runtime paths shared by every command; importing the package creates no files."""

import os
from pathlib import Path


def data_directory() -> Path:
    configured = os.environ.get("THREATLENS_DATA_DIR")
    return Path(configured).expanduser() if configured else Path.home() / ".threatlens"


def database_path() -> Path:
    return data_directory() / "threatlens.db"
