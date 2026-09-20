from typing import Any


def calculate_delta(current: float, previous: float) -> float:
    """Calculate the difference between two observations."""
    return current - previous


def extract_network_temporal_features(
    current: dict[str, Any],
    previous: dict[str, Any],
) -> dict[str, float]:
    """Extract behavioral changes between network snapshots."""

    current_features = current.get("features", current)
    previous_features = previous.get("features", previous)

    return {
        "connection_delta": calculate_delta(
            float(current_features.get("connection_count", 0.0)),
            float(previous_features.get("connection_count", 0.0)),
        ),
        "tcp_connection_delta": calculate_delta(
            float(current_features.get("tcp_connection_count", 0.0)),
            float(previous_features.get("tcp_connection_count", 0.0)),
        ),
        "udp_connection_delta": calculate_delta(
            float(current_features.get("udp_connection_count", 0.0)),
            float(previous_features.get("udp_connection_count", 0.0)),
        ),
        "established_connection_delta": calculate_delta(
            float(
                current_features.get(
                    "established_connection_count", 0.0
                )
            ),
            float(
                previous_features.get(
                    "established_connection_count", 0.0
                )
            ),
        ),
        "listening_port_delta": calculate_delta(
            float(
                current_features.get(
                    "listening_port_count", 0.0
                )
            ),
            float(
                previous_features.get(
                    "listening_port_count", 0.0
                )
            ),
        ),
        "unique_remote_address_delta": calculate_delta(
            float(
                current_features.get(
                    "unique_remote_addresses", 0.0
                )
            ),
            float(
                previous_features.get(
                    "unique_remote_addresses", 0.0
                )
            ),
        ),
        "unique_remote_port_delta": calculate_delta(
            float(
                current_features.get(
                    "unique_remote_ports", 0.0
                )
            ),
            float(
                previous_features.get(
                    "unique_remote_ports", 0.0
                )
            ),
        ),
    }
