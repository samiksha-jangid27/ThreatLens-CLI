import sqlite3
from pathlib import Path


class ThreatLensDatabase:
    """Manage the local ThreatLens SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def connect(self) -> sqlite3.Connection:
        """Open a connection to the SQLite database."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Pre-create with private permissions before SQLite opens it.
        import os
        descriptor = os.open(self.database_path, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(descriptor)
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Create the ThreatLens database schema."""
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    severity TEXT NOT NULL,
                    is_suspicious INTEGER NOT NULL,
                    signals TEXT NOT NULL
                )
                """
            )

            connection.commit()
