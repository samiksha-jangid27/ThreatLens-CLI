"""Local adapter; device imports use the same aggregate feature contract."""

import platform
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import psutil

from threatlens.collectors.network import collect_network_telemetry
from threatlens.collectors.processes import collect_process_telemetry
from threatlens.collectors.system import collect_system_telemetry
from threatlens.features.network import extract_network_features
from threatlens.features.process import extract_process_features
from threatlens.features.system import extract_system_features
from threatlens.ingestion.validator import validate_system_telemetry
from threatlens.schema.device import DeviceObservation


def local_device_id() -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]", "_", platform.node()).strip("_.:-")[:128] or "local-host"


def collect_device_observation(device_id: str | None = None) -> DeviceObservation:
    sources, unavailable = {}, {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        pending = {
            "system": executor.submit(collect_system_telemetry),
            "network": executor.submit(collect_network_telemetry),
            "process": executor.submit(collect_process_telemetry),
        }
        for name, future in pending.items():
            try:
                data = future.result()
                if name == "system":
                    validate_system_telemetry(data.to_dict())
                    sources[name] = extract_system_features(data.to_dict())
                elif name == "network":
                    sources[name] = extract_network_features(data)
                elif not data.get("available", True):
                    unavailable[name] = data.get("error") or "Incomplete process telemetry"
                else:
                    sources[name] = extract_process_features(data)
            except (psutil.Error, PermissionError, OSError, ValueError) as error:
                unavailable[name] = f"{name} unavailable: {type(error).__name__}"
    if not sources:
        raise ValueError("No telemetry available; check OS permissions or supply --input")
    return DeviceObservation(
        device_id or local_device_id(),
        "system",
        datetime.now(UTC).isoformat(),
        1.0,
        sources,
        unavailable,
    )
