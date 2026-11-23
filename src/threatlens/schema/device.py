"""Versioned, vendor-neutral behavioral telemetry contract.

Metrics describe an observation window, not lifetime counters. Missing sources
are explicit so collection failures can never masquerade as zero activity.
"""

import re
from dataclasses import asdict, dataclass
from datetime import datetime
from math import isfinite
from typing import Any

DEVICE_SOURCES = {
    "system": {"system", "network", "process"},
    "router": {"system", "network", "routing"},
    "firewall": {"system", "network", "firewall"},
    "network": {"network"},
}
# A small, documented metric vocabulary makes feature meaning stable across imports.
SOURCE_FEATURES = {
    "system": {
        "cpu_percent",
        "memory_percent",
        "memory_available_mb",
        "load_average_1m",
        "process_count",
        "disk_percent",
    },
    "network": {
        "connection_count",
        "tcp_connection_count",
        "udp_connection_count",
        "established_connection_count",
        "listening_connection_count",
        "listening_port_count",
        "unique_remote_addresses",
        "unique_remote_ports",
        "unique_local_ports",
        "bytes_in",
        "bytes_out",
        "packets_in",
        "packets_out",
        "dropped_packets",
    },
    "process": {
        "total_processes",
        "unique_process_names",
        "unique_users",
        "high_cpu_process_count",
        "high_memory_process_count",
        "root_process_count",
        "running_process_count",
        "sleeping_process_count",
        "stopped_process_count",
        "unique_parent_processes",
        "average_cpu_percent",
        "average_memory_percent",
    },
    "routing": {
        "route_count",
        "route_changes",
        "neighbor_changes",
        "interface_errors",
        "interface_flaps",
    },
    "firewall": {
        "active_sessions",
        "new_sessions",
        "denied_connections",
        "allowed_connections",
        "policy_changes",
        "authentication_failures",
    },
}


@dataclass(frozen=True)
class DeviceObservation:
    device_id: str
    device_type: str
    timestamp: str
    window_seconds: float
    sources: dict[str, dict[str, float]]
    unavailable: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def timestamp_value(value: Any) -> datetime:
    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None:
            raise ValueError("missing timezone")
        return result
    except (TypeError, ValueError) as error:
        raise ValueError("timestamp must be an ISO-8601 datetime with timezone") from error


def parse_document(data: Any) -> list[DeviceObservation]:
    if not isinstance(data, dict) or set(data) != {
        "schema_version",
        "device_id",
        "device_type",
        "observations",
    }:
        raise ValueError("Expected schema_version, device_id, device_type, observations")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported schema_version (expected 1)")
    device_id, device_type = data["device_id"], data["device_type"]
    if not isinstance(device_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", device_id
    ):
        raise ValueError(
            "device_id must be 1-128 ASCII letters, digits, dots, colons, hyphens or underscores"
        )
    if not isinstance(device_type, str) or device_type not in DEVICE_SOURCES:
        raise ValueError("device_type must be system, router, firewall, or network")
    rows = data["observations"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 2000:
        raise ValueError("observations must contain 1-2000 windows")
    result = []
    previous = None
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "timestamp",
            "window_seconds",
            "sources",
            "unavailable",
        }:
            raise ValueError(
                "Each observation requires timestamp, window_seconds, sources, unavailable"
            )
        stamp = timestamp_value(row["timestamp"])
        if previous is not None and stamp <= previous:
            raise ValueError("Observation timestamps must be strictly increasing")
        previous = stamp
        window = row["window_seconds"]
        if (
            isinstance(window, bool)
            or not isinstance(window, (int, float))
            or not isfinite(window)
            or not 0 < window <= 86400
        ):
            raise ValueError("window_seconds must be finite and in (0, 86400]")
        sources, unavailable = row["sources"], row["unavailable"]
        if not isinstance(sources, dict) or not sources or not isinstance(unavailable, dict):
            raise ValueError("sources must be nonempty and unavailable must be an object")
        allowed = DEVICE_SOURCES[device_type]
        if (set(sources) | set(unavailable)) - allowed or set(sources) & set(unavailable):
            raise ValueError("Invalid, overlapping, or unsupported telemetry sources")
        for reason in unavailable.values():
            if (
                not isinstance(reason, str)
                or not 1 <= len(reason) <= 500
                or any(ord(c) < 32 for c in reason)
            ):
                raise ValueError("Unavailable source reason must be 1-500 printable characters")
        clean = {}
        for source, metrics in sources.items():
            if (
                not isinstance(metrics, dict)
                or not metrics
                or set(metrics) - SOURCE_FEATURES[source]
            ):
                raise ValueError(f"Unsupported or empty {source} feature set")
            clean[source] = {}
            for name, value in metrics.items():
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not isfinite(value)
                    or not 0 <= value <= 1e15
                ):
                    raise ValueError(f"{source}.{name} must be a finite nonnegative number <= 1e15")
                if (
                    name
                    in {"cpu_percent", "memory_percent", "disk_percent", "average_memory_percent"}
                    and value > 100
                ):
                    raise ValueError(f"{name} must be <= 100")
                clean[source][name] = float(value)
        result.append(
            DeviceObservation(
                device_id, device_type, stamp.isoformat(), float(window), clean, dict(unavailable)
            )
        )
    return result
