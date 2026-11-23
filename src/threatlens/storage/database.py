import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class ThreatLensDatabase:
    """Local transactional state with additive migration from the original schema."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(self.database_path, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(descriptor)
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    severity TEXT NOT NULL,
                    is_suspicious INTEGER NOT NULL,
                    signals TEXT NOT NULL
                )
            """)
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(incidents)")}
            if "detection" not in columns:
                connection.execute("ALTER TABLE incidents ADD COLUMN detection TEXT NOT NULL DEFAULT '{}'")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS device_state (
                    device_key TEXT PRIMARY KEY,
                    state TEXT NOT NULL
                )
            """)
