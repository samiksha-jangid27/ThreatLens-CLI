# Telemetry contract and adapters

The canonical input is UTF-8 JSON, schema version 1. Use `collect` for local exports, `import-zeek` for supported connection logs, or map your device's exported metrics to this contract. The files under `examples/` are synthetic and reproducible with `python scripts/generate_examples.py`.

```json
{
  "schema_version": 1,
  "device_id": "lab-router",
  "device_type": "router",
  "observations": [
    {
      "timestamp": "2026-01-01T00:00:00+00:00",
      "window_seconds": 60,
      "sources": {
        "network": {"bytes_out": 10000, "packets_out": 100},
        "routing": {"route_count": 100, "route_changes": 2}
      },
      "unavailable": {}
    }
  ]
}
```

## Validation and profile identity

Root and observation keys must match the contract exactly. Input is limited to 10 MiB and 1-2000 observations. Device IDs contain 1-128 ASCII letters, digits, dots, colons, hyphens or underscores, beginning with a letter or digit. The baseline key combines device type and ID. Use a stable ID for the same sensor and profile; do not mix sensors, vantage points or units under one ID.

Timestamps are ISO 8601 with a timezone and strictly increasing within a batch. An assessment timestamp must also be later than the previously stored observation. Windows are finite numbers in (0, 86400] seconds and must match the learned profile. The parser does not validate clock authenticity or require past dates, so exported timestamps remain an operator responsibility.

Every observation has at least one nonempty `sources` map. `unavailable` maps a supported source to a printable reason, for example `{"network":"OS denied connection access"}`. A source cannot appear in both maps. A missing trained source is degraded, not zero activity. Explicit learning refuses declared unavailable sources. A source deliberately excluded from a profile is outside its detection scope.

All feature values are real JSON numbers, finite, nonnegative and at most 1e15. Booleans, numeric strings, duplicate JSON keys and nonfinite values are rejected. System CPU, memory and disk percentages, and average process memory percentage, cannot exceed 100. Process CPU averages may exceed 100 for multithreaded processes. Unknown feature names are rejected. Each source may use a subset of its vocabulary; its exact keys must then remain stable across learning and scans.

| Device type | Supported source domains |
| --- | --- |
| system | system, network, process |
| router | system, network, routing |
| firewall | system, network, firewall |
| network | network |

## Units and meaning

Gauge fields describe the sampled state. Count and byte fields describing events must be computed for the declared window, not copied from lifetime counters. Derive counter differences upstream, handle resets, and use a separate device ID if metric semantics change. Do not claim a missing vendor metric is zero.

- **system**: `cpu_percent`, `memory_percent`, `disk_percent` are utilization percentages; `memory_available_mb` is available memory in MiB; `load_average_1m` is the 1-minute load; `process_count` is a count. Uptime is excluded from behavioral features.
- **network gauges or window counts**: `connection_count`, `tcp_connection_count`, `udp_connection_count`, `established_connection_count`, `listening_connection_count`, `listening_port_count`, `unique_remote_addresses`, `unique_remote_ports`, `unique_local_ports`. Local collectors use socket snapshot counts. Flow imports use completed-flow counts grouped by connection start time, so they require a separate profile.
- **network window totals**: `bytes_in`, `bytes_out`, `packets_in`, `packets_out`, `dropped_packets`.
- **process**: `total_processes`, `unique_process_names`, `unique_users`, `high_cpu_process_count`, `high_memory_process_count`, `root_process_count`, `running_process_count`, `sleeping_process_count`, `stopped_process_count`, `unique_parent_processes`, `average_cpu_percent`, `average_memory_percent`. Heavy CPU means at least 50%; heavy memory means at least 10% of host memory.
- **routing**: `route_count` is a gauge; `route_changes`, `neighbor_changes`, `interface_errors`, `interface_flaps` are window event counts.
- **firewall**: `active_sessions` is a gauge; `new_sessions`, `denied_connections`, `allowed_connections`, `policy_changes`, `authentication_failures` are window event counts.

The code's authoritative vocabulary is `schema/device.py`. Generic numeric range validation does not establish that the supplied telemetry is truthful or physically consistent. Vendor APIs, interface selection, counter reconciliation and authentication are adapter responsibilities.

## Zeek adapter

`import-zeek` supports uncompressed TSV `conn.log` with a tab-separated `#fields` header. Required columns are `ts`, `id.orig_h`, `id.resp_h`, `id.orig_p`, `id.resp_p`, `proto`, `orig_bytes`, and `resp_bytes`. Additional columns are ignored. Missing required values (`-`), invalid addresses, invalid ports, unknown protocols and malformed rows stop conversion rather than silently filling zeros. JSON-formatted Zeek logs and compressed files are not supported by this adapter.

Epoch timestamps are grouped into UTC-aligned buckets. `bytes_out` means originator bytes and `bytes_in` means responder bytes, independent of local/internet direction. Remote address/port counts refer to responders. Complete connection totals are assigned to the connection's start bucket, including for long connections; they are not per-bucket interface throughput. Only occupied buckets are emitted, so missing buckets do not assert that a sensor was healthy and idle. Out-of-order log records are sorted by bucket; replay protection applies when the converted observations are assessed.

Train on an earlier trusted log and scan a later held-out log with the same sensor ID and window length. Do not train and scan the same windows. See the [Zeek connection reference](https://docs.zeek.org/en/current/reference/logs/conn.html) and [TSV log documentation](https://docs.zeek.org/en/current/tutorial/logs.html) for upstream field definitions.
