from typing import Any


def extract_process_features(
    process_data: dict[str, Any],
    cpu_threshold: float = 50.0,
    memory_threshold: float = 10.0,
) -> dict[str, float]:
    """Extract behavioral features from process telemetry."""

    processes = process_data.get("processes", [])

    unique_names: set[str] = set()
    unique_users: set[str] = set()

    high_cpu_process_count = 0
    high_memory_process_count = 0
    root_process_count = 0

    for process in processes:
        name = process.get("name")

        if name:
            unique_names.add(str(name))

        username = process.get("username")

        if username:
            unique_users.add(str(username))

        cpu_percent = float(
            process.get("cpu_percent", 0.0)
        )

        memory_percent = float(
            process.get("memory_percent", 0.0)
        )

        if cpu_percent >= cpu_threshold:
            high_cpu_process_count += 1

        if memory_percent >= memory_threshold:
            high_memory_process_count += 1

        if username == "root":
            root_process_count += 1

    return {
        "total_processes": float(len(processes)),
        "unique_process_names": float(len(unique_names)),
        "unique_users": float(len(unique_users)),
        "high_cpu_process_count": float(
            high_cpu_process_count
        ),
        "high_memory_process_count": float(
            high_memory_process_count
        ),
        "root_process_count": float(root_process_count),
    }
