from typing import Any


def extract_process_features(
    process_data: dict[str, Any],
    cpu_threshold: float = 50.0,
    memory_threshold: float = 10.0,
) -> dict[str, float]:
    """
    Extract behavioral features from process telemetry.
    """

    processes = process_data.get(
        "processes",
        [],
    )

    unique_names: set[str] = set()
    unique_users: set[str] = set()

    high_cpu_process_count = 0
    high_memory_process_count = 0
    root_process_count = 0

    running_process_count = 0
    sleeping_process_count = 0
    stopped_process_count = 0

    parent_process_ids: set[int] = set()

    total_cpu_percent = 0.0
    total_memory_percent = 0.0

    for process in processes:
        name = process.get("name")

        if name:
            unique_names.add(
                str(name)
            )

        username = process.get(
            "username"
        )

        if username:
            unique_users.add(
                str(username)
            )

        cpu_percent = float(
            process.get(
                "cpu_percent",
                0.0,
            )
        )

        memory_percent = float(
            process.get(
                "memory_percent",
                0.0,
            )
        )

        total_cpu_percent += cpu_percent
        total_memory_percent += memory_percent

        if cpu_percent >= cpu_threshold:
            high_cpu_process_count += 1

        if memory_percent >= memory_threshold:
            high_memory_process_count += 1

        if username == "root":
            root_process_count += 1

        status = str(
            process.get(
                "status",
                "",
            )
        ).lower()

        if status == "running":
            running_process_count += 1

        elif status == "sleeping":
            sleeping_process_count += 1

        elif status in {
            "stopped",
            "tracing-stop",
        }:
            stopped_process_count += 1

        parent_pid = process.get(
            "parent_pid"
        )

        if parent_pid is not None:
            parent_process_ids.add(
                int(parent_pid)
            )

    process_count = len(processes)

    average_cpu_percent = (
        total_cpu_percent / process_count
        if process_count
        else 0.0
    )

    average_memory_percent = (
        total_memory_percent / process_count
        if process_count
        else 0.0
    )

    return {
        "total_processes": float(
            process_count
        ),
        "unique_process_names": float(
            len(unique_names)
        ),
        "unique_users": float(
            len(unique_users)
        ),
        "high_cpu_process_count": float(
            high_cpu_process_count
        ),
        "high_memory_process_count": float(
            high_memory_process_count
        ),
        "root_process_count": float(
            root_process_count
        ),
        "running_process_count": float(
            running_process_count
        ),
        "sleeping_process_count": float(
            sleeping_process_count
        ),
        "stopped_process_count": float(
            stopped_process_count
        ),
        "unique_parent_processes": float(
            len(parent_process_ids)
        ),
        "average_cpu_percent": float(
            average_cpu_percent
        ),
        "average_memory_percent": float(
            average_memory_percent
        ),
    }