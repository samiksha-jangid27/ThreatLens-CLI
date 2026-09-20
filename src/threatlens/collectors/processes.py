from datetime import datetime, timezone
from typing import Any

import psutil

from threatlens.schema.process import ProcessTelemetry


def collect_process_telemetry() -> dict[str, Any]:
    """Collect telemetry for currently running processes."""

    processes: list[ProcessTelemetry] = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "username",
            "cpu_percent",
            "memory_percent",
            "status",
            "ppid",
        ]
    ):
        try:
            info = process.info

            processes.append(
                ProcessTelemetry(
                    pid=int(info["pid"]),
                    name=str(info["name"] or "unknown"),
                    username=(
                        str(info["username"])
                        if info["username"] is not None
                        else None
                    ),
                    cpu_percent=float(info["cpu_percent"] or 0.0),
                    memory_percent=float(
                        info["memory_percent"] or 0.0
                    ),
                    status=str(info["status"] or "unknown"),
                    parent_pid=(
                        int(info["ppid"])
                        if info["ppid"] is not None
                        else None
                    ),
                )
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            # A process can disappear or become inaccessible
            # while the snapshot is being collected.
            continue

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "process_count": len(processes),
        "processes": [
            process.to_dict()
            for process in processes
        ],
    }