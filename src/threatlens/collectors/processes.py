import time
from datetime import UTC, datetime
from typing import Any

import psutil

from threatlens.schema.process import ProcessTelemetry


def collect_process_telemetry() -> dict[str, Any]:
    """Measure process CPU over one second; discard first-call zero readings."""
    candidates = list(psutil.process_iter())
    sampled = []
    skipped = 0
    for process in candidates:
        try:
            process.cpu_percent(None)
            sampled.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            skipped += 1
    time.sleep(1)
    processes = []
    for process in sampled:
        try:
            info = process.as_dict(
                attrs=["pid", "name", "username", "memory_percent", "status", "ppid"]
            )
            cpu = process.cpu_percent(None)
            if any(info[name] is None for name in ("pid", "memory_percent", "username", "ppid")):
                skipped += 1
                continue
            processes.append(
                ProcessTelemetry(
                    pid=int(info["pid"]),
                    name=str(info["name"] or "unknown"),
                    username=info["username"],
                    cpu_percent=float(cpu),
                    memory_percent=float(info["memory_percent"]),
                    status=str(info["status"] or "unknown"),
                    parent_pid=int(info["ppid"]),
                ).to_dict()
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            skipped += 1
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "process_count": len(processes),
        "processes": processes,
        "skipped_processes": skipped,
        "available": skipped == 0,
        "error": f"{skipped} processes inaccessible or exited" if skipped else None,
    }
