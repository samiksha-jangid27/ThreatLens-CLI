from typing import Any

from threatlens.schema.network import NetworkTelemetry


def extract_network_features(
    network_data: NetworkTelemetry | dict[str, Any],
) -> dict[str, float]:
    """
    Extract behavioral features from network telemetry.

    Supports both NetworkTelemetry objects and
    serialized dictionary observations.
    """

    if isinstance(network_data, NetworkTelemetry):
        connections = [
            connection.to_dict()
            for connection in network_data.connections
        ]

        connection_count = float(
            network_data.connection_count
        )

        tcp_connection_count = float(
            network_data.tcp_connection_count
        )

        udp_connection_count = float(
            network_data.udp_connection_count
        )

        listening_port_count = float(
            network_data.listening_port_count
        )

    else:
        connections = network_data.get(
            "connections",
            [],
        )

        connection_count = float(
            network_data.get(
                "connection_count",
                len(connections),
            )
        )

        tcp_connection_count = float(
            network_data.get(
                "tcp_connection_count",
                0,
            )
        )

        udp_connection_count = float(
            network_data.get(
                "udp_connection_count",
                0,
            )
        )

        listening_port_count = float(
            network_data.get(
                "listening_port_count",
                0,
            )
        )

    established_connection_count = 0
    listening_connection_count = 0

    remote_addresses: set[str] = set()
    remote_ports: set[int] = set()
    local_ports: set[int] = set()

    for connection in connections:
        status = str(
            connection.get(
                "status",
                "",
            )
        ).upper()

        if status == "ESTABLISHED":
            established_connection_count += 1

        if status == "LISTEN":
            listening_connection_count += 1

        remote_address = connection.get(
            "remote_address"
        )

        if remote_address:
            remote_addresses.add(
                str(remote_address)
            )

        remote_port = connection.get(
            "remote_port"
        )

        if remote_port is not None:
            remote_ports.add(
                int(remote_port)
            )

        local_port = connection.get(
            "local_port"
        )

        if local_port is not None:
            local_ports.add(
                int(local_port)
            )

    return {
        "connection_count": connection_count,
        "tcp_connection_count": tcp_connection_count,
        "udp_connection_count": udp_connection_count,
        "established_connection_count": float(
            established_connection_count
        ),
        "listening_connection_count": float(
            listening_connection_count
        ),
        "listening_port_count": listening_port_count,
        "unique_remote_addresses": float(
            len(remote_addresses)
        ),
        "unique_remote_ports": float(
            len(remote_ports)
        ),
        "unique_local_ports": float(
            len(local_ports)
        ),
    }