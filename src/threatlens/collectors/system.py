from datetime import UTC, datetime
from pathlib import Path

import psutil

from threatlens.schema.telemetry import SystemTelemetry


def collect_system_telemetry() -> SystemTelemetry:
    """Collect basic system telemetry."""

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(Path.home().anchor)

    now = datetime.now(UTC)

    cpu = psutil.cpu_percent(interval=1)
    now = datetime.now(UTC)
    return SystemTelemetry(
        timestamp=now,
        cpu_percent=cpu,
        memory_percent=memory.percent,
        memory_available_mb=round(memory.available / (1024 * 1024), 2),
        load_average_1m=psutil.getloadavg()[0],
        process_count=len(psutil.pids()),
        uptime_seconds=int(now.timestamp() - psutil.boot_time()),
        disk_percent=disk.percent,
    )
