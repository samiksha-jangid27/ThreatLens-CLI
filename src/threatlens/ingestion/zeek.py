"""Convert Zeek conn.log TSV records into bounded observation windows.

This adapter reads exported logs. It never captures traffic or contacts devices.
"""

import ipaddress
from collections import defaultdict
from datetime import UTC, datetime
from math import isfinite
from pathlib import Path

from threatlens.ingestion.device import MAX_INPUT_BYTES
from threatlens.schema.device import parse_document

REQUIRED = {
    "ts",
    "id.orig_h",
    "id.resp_h",
    "id.orig_p",
    "id.resp_p",
    "proto",
    "orig_bytes",
    "resp_bytes",
}


def convert_zeek(path: Path, device_id: str, window_seconds: int = 60) -> dict:
    if not 1 <= window_seconds <= 86400:
        raise ValueError("window_seconds must be between 1 and 86400")
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("Zeek input exceeds 10 MiB")
    fields = None
    buckets = defaultdict(list)
    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if line.startswith("#fields\t"):
            fields = line.split("\t")[1:]
            if len(set(fields)) != len(fields) or not REQUIRED.issubset(fields):
                raise ValueError("Zeek #fields header is missing required fields or has duplicates")
            continue
        if not line or line.startswith("#"):
            continue
        if fields is None:
            raise ValueError("Expected a tab-separated Zeek #fields header before records")
        values = line.split("\t")
        if len(values) != len(fields):
            raise ValueError(f"Zeek line {number}: record width differs from #fields")
        row = dict(zip(fields, values, strict=True))
        try:
            stamp = float(row["ts"])
            if not isfinite(stamp) or not 0 <= stamp <= 253402300799:
                raise ValueError("invalid epoch timestamp")
            # Validate rather than retaining or interpreting endpoints as IoCs.
            ipaddress.ip_address(row["id.orig_h"])
            ipaddress.ip_address(row["id.resp_h"])
            for name in ("id.orig_p", "id.resp_p"):
                if not 0 <= int(row[name]) <= 65535:
                    raise ValueError("invalid port")
            for name in ("orig_bytes", "resp_bytes"):
                if not 0 <= int(row[name]) <= 10**15:
                    raise ValueError("invalid byte count")
            if row["proto"] not in {"tcp", "udp", "icmp"}:
                raise ValueError("unsupported protocol")
        except (ValueError, OverflowError) as error:
            raise ValueError(f"Zeek line {number}: {error}") from error
        buckets[int(stamp // window_seconds) * window_seconds].append(row)
        if len(buckets) > 2000:
            raise ValueError("Zeek input spans more than 2000 occupied windows")
    if not buckets:
        raise ValueError("Zeek input has no connection records")
    observations = []
    for start, rows in sorted(buckets.items()):
        metrics = {
            "connection_count": len(rows),
            "tcp_connection_count": sum(row["proto"] == "tcp" for row in rows),
            "udp_connection_count": sum(row["proto"] == "udp" for row in rows),
            "unique_remote_addresses": len({row["id.resp_h"] for row in rows}),
            "unique_remote_ports": len({row["id.resp_p"] for row in rows}),
            "bytes_out": sum(int(row["orig_bytes"]) for row in rows),
            "bytes_in": sum(int(row["resp_bytes"]) for row in rows),
        }
        observations.append(
            {
                "timestamp": datetime.fromtimestamp(start, UTC).isoformat(),
                "window_seconds": window_seconds,
                "sources": {"network": metrics},
                "unavailable": {},
            }
        )
    document = {
        "schema_version": 1,
        "device_type": "network",
        "device_id": device_id,
        "observations": observations,
    }
    parse_document(document)
    return document
