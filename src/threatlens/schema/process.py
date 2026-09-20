from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProcessTelemetry:
    """Represent telemetry for a running process."""

    pid: int
    name: str
    username: str | None
    cpu_percent: float
    memory_percent: float
    status: str
    parent_pid: int | None

    def to_dict(self) -> dict[str, Any]:
        """Convert process telemetry into a serializable dictionary."""
        return {
            "pid": self.pid,
            "name": self.name,
            "username": self.username,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "status": self.status,
            "parent_pid": self.parent_pid,
        }