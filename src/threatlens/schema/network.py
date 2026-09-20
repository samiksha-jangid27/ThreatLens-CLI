from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class NetworkConnection:
    """Represent one observed network connection."""

    local_address: str
    local_port: int
    remote_address: str | None
    remote_port: int | None
    status: str
    protocol: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the connection into a serializable dictionary."""
        return {
            "local_address": self.local_address,
            "local_port": self.local_port,
            "remote_address": self.remote_address,
            "remote_port": self.remote_port,
            "status": self.status,
            "protocol": self.protocol,
        }


@dataclass(frozen=True)
class NetworkTelemetry:
    """Represent a snapshot of network behavior."""

    timestamp: datetime
    connection_count: int
    tcp_connection_count: int
    udp_connection_count: int
    listening_port_count: int
    connections: tuple[NetworkConnection, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert network telemetry into a serializable dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "connection_count": self.connection_count,
            "tcp_connection_count": self.tcp_connection_count,
            "udp_connection_count": self.udp_connection_count,
            "listening_port_count": self.listening_port_count,
            "connections": [
                connection.to_dict()
                for connection in self.connections
            ],
        }
