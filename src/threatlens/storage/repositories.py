import json
import sqlite3
from typing import Any

from threatlens.storage.database import ThreatLensDatabase


class IncidentRepository:
    """Store the original evidence, not just an alert's signal names."""

    def __init__(self, database: ThreatLensDatabase) -> None:
        self.database = database
        self.database.initialize()

    def create(
        self, detection_result: dict[str, Any], connection: sqlite3.Connection | None = None
    ) -> int:
        if connection is None:
            with self.database.connect() as opened:
                return self.create(detection_result, opened)
        risk = detection_result["risk"]
        cursor = connection.execute(
            """
            INSERT INTO incidents (timestamp, risk_score, severity, is_suspicious, signals, detection)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                detection_result.get("timestamp", ""),
                float(risk["risk_score"]),
                str(risk["severity"]),
                int(bool(detection_result["is_suspicious"])),
                json.dumps(detection_result.get("signals", {}), allow_nan=False),
                json.dumps(detection_result, allow_nan=False),
            ),
        )
        return int(cursor.lastrowid)

    def get(self, incident_id: int) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return self._deserialize(row) if row is not None else None

    def list_all(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
        return [self._deserialize(row) for row in rows]

    @staticmethod
    def _deserialize(row: Any) -> dict[str, Any]:
        return {
            **json.loads(row["detection"]),
            "id": int(row["id"]),
            "timestamp": row["timestamp"],
            "risk_score": float(row["risk_score"]),
            "severity": row["severity"],
            "is_suspicious": bool(row["is_suspicious"]),
            "signals": json.loads(row["signals"]),
        }
