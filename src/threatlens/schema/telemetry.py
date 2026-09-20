from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SystemTelemetry:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    load_average_1m: float
    process_count: int
    uptime_seconds: int
    disk_percent: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_available_mb": self.memory_available_mb,
            "load_average_1m": self.load_average_1m,
            "process_count": self.process_count,
            "uptime_seconds": self.uptime_seconds,
            "disk_percent": self.disk_percent,
        }