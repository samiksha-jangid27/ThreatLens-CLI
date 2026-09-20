from datetime import datetime, timezone

import psutil


def collect_system_telemetry() -> dict:
    """Collect basic Linux system telemetry."""

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": memory.percent,
        "memory_available_mb": round(memory.available / (1024 * 1024), 2),
        "load_average_1m": psutil.getloadavg()[0],
        "process_count": len(psutil.pids()),
        "uptime_seconds": int(
            datetime.now(timezone.utc).timestamp()
            - psutil.boot_time()
        ),
        "disk_percent": disk.percent,
    }