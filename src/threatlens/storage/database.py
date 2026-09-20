import sqlite3
from pathlib import Path


class ThreatLensDatabase:
    """Manage the local ThreatLens SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def connect(self) -> sqlite3.Connection:
        """Open a connection to the SQLite database."""
        connection = sqlite3.connect(self.database_path)
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
