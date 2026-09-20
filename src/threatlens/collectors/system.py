from datetime import datetime, timezone

import psutil

from threatlens.schema.telemetry import SystemTelemetry


def collect_system_telemetry() -> SystemTelemetry:
    """Collect basic system telemetry."""

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    now = datetime.now(timezone.utc)

    return SystemTelemetry(
        timestamp=now,
        cpu_percent=psutil.cpu_percent(interval=1),
        memory_percent=memory.percent,
        memory_available_mb=round(memory.available / (1024 * 1024), 2),
        load_average_1m=psutil.getloadavg()[0],
        process_count=len(psutil.pids()),
        uptime_seconds=int(now.timestamp() - psutil.boot_time()),
        disk_percent=disk.percent,
    )