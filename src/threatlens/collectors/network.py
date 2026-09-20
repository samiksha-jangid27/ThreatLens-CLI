from datetime import datetime, timezone

import psutil

from threatlens.schema.network import (
    NetworkConnection,
    NetworkTelemetry,
)


def _extract_address(address: object) -> tuple[str, int]:
    """Extract host and port from a psutil address object."""
    if not address:
        return "", 0

    return str(address.ip), int(address.port)


def collect_network_telemetry() -> NetworkTelemetry:
    """Collect a snapshot of local network connection behavior."""

    connections: list[NetworkConnection] = []

    tcp_count = 0
    udp_count = 0
    listening_ports: set[int] = set()

    try:
        raw_connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        raw_connections = []

    for connection in raw_connections:
        local_address, local_port = _extract_address(connection.laddr)

        remote_address = None
        remote_port = None

        if connection.raddr:
            remote_address, remote_port = _extract_address(
                connection.raddr
            )

        protocol = "tcp" if connection.type == 1 else "udp"

        if protocol == "tcp":
            tcp_count += 1
        else:
            udp_count += 1

        if connection.status == psutil.CONN_LISTEN:
            listening_ports.add(local_port)

        connections.append(
            NetworkConnection(
                local_address=local_address,
                local_port=local_port,
                remote_address=remote_address,
                remote_port=remote_port,
                status=connection.status,
                protocol=protocol,
            )
        )

    return NetworkTelemetry(
        timestamp=datetime.now(timezone.utc),
        connection_count=len(connections),
        tcp_connection_count=tcp_count,
        udp_connection_count=udp_count,
        listening_port_count=len(listening_ports),
        connections=tuple(connections),
    )