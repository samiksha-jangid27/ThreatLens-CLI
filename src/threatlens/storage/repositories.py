import json
from typing import Any

from threatlens.storage.database import ThreatLensDatabase


class IncidentRepository:
    """Store and retrieve ThreatLens detection incidents."""

    def __init__(self, database: ThreatLensDatabase) -> None:
        self.database = database
        self.database.initialize()

    def create(
        self,
        detection_result: dict[str, Any],
    ) -> int:
        """Persist a detection result and return its incident ID."""

        risk = detection_result["risk"]
        correlation = detection_result["correlation"]

        signals = json.dumps(
            detection_result.get("signals", {})
        )

        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO incidents (
                    timestamp,
                    risk_score,
                    severity,
                    is_suspicious,
                    signals
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    detection_result.get("timestamp", ""),
                    float(risk["risk_score"]),
                    str(risk["severity"]),
                    int(
                        bool(
                            detection_result["is_suspicious"]
                        )
                    ),
                    signals,
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

    def get(self, incident_id: int) -> dict[str, Any] | None:
        """Retrieve one incident by ID."""

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    timestamp,
                    risk_score,
                    severity,
                    is_suspicious,
                    signals
                FROM incidents
                WHERE id = ?
                """,
                (incident_id,),
            ).fetchone()

        if row is None:
            return None

        return self._deserialize(row)

    def list_all(self) -> list[dict[str, Any]]:
        """Return all stored incidents."""

        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    timestamp,
                    risk_score,
                    severity,
                    is_suspicious,
                    signals
                FROM incidents
                ORDER BY id DESC
                """
            ).fetchall()

        return [
            self._deserialize(row)
            for row in rows
        ]

    @staticmethod
    def _deserialize(row: Any) -> dict[str, Any]:
        """Convert a database row into a normal dictionary."""

        return {
            "id": int(row["id"]),
            "timestamp": row["timestamp"],
            "risk_score": float(row["risk_score"]),
            "severity": row["severity"],
            "is_suspicious": bool(row["is_suspicious"]),
            "signals": json.loads(row["signals"]),
        }
