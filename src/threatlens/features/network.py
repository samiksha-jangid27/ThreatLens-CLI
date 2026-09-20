from typing import Any

from threatlens.schema.network import NetworkTelemetry


def extract_network_features(
    network_data: NetworkTelemetry | dict[str, Any],
) -> dict[str, float]:
    """Extract behavioral features from network telemetry."""

    if isinstance(network_data, NetworkTelemetry):
        connections = [
            connection.to_dict()
            for connection in network_data.connections
        ]
    else:
        connections = network_data.get("connections", [])

    unique_remote_addresses: set[str] = set()
    unique_remote_ports: set[int] = set()
    unique_local_ports: set[int] = set()
    listening_ports: set[int] = set()

    established_connection_count = 0
    listening_connection_count = 0

    tcp_connection_count = 0
    udp_connection_count = 0

    for connection in connections:
        protocol = str(
            connection.get("protocol", "")
        ).lower()

        if protocol == "tcp":
            tcp_connection_count += 1
        elif protocol == "udp":
            udp_connection_count += 1

        remote_address = connection.get("remote_address")

        if remote_address:
            unique_remote_addresses.add(
                str(remote_address)
            )

        remote_port = connection.get("remote_port")

        if remote_port is not None:
            unique_remote_ports.add(int(remote_port))

        local_port = connection.get("local_port")

        if local_port is not None:
            local_port = int(local_port)
            unique_local_ports.add(local_port)

        status = str(
            connection.get("status", "")
        ).upper()

        if status == "ESTABLISHED":
            established_connection_count += 1

        if status == "LISTEN":
            listening_connection_count += 1
            listening_ports.add(local_port)

    return {
        "connection_count": float(len(connections)),
        "tcp_connection_count": float(tcp_connection_count),
        "udp_connection_count": float(udp_connection_count),
        "established_connection_count": float(
            established_connection_count
        ),
        "listening_connection_count": float(
            listening_connection_count
        ),
        "unique_remote_addresses": float(
            len(unique_remote_addresses)
        ),
        "unique_remote_ports": float(
            len(unique_remote_ports)
        ),
        "unique_local_ports": float(
            len(unique_local_ports)
        ),
        "listening_port_count": float(
            len(listening_ports)
        ),
    }