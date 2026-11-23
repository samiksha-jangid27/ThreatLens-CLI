from datetime import datetime

from threatlens.collectors.network import collect_network_telemetry
from threatlens.schema.network import NetworkConnection, NetworkTelemetry


def test_network_collector_returns_network_telemetry(fake_host):
    telemetry = collect_network_telemetry()

    assert isinstance(telemetry, NetworkTelemetry)
    assert isinstance(telemetry.timestamp, datetime)
    assert telemetry.connection_count >= 0
    assert telemetry.tcp_connection_count >= 0
    assert telemetry.udp_connection_count >= 0
    assert telemetry.listening_port_count >= 0


def test_network_connection_serializes_correctly(fake_host):
    connection = NetworkConnection(
        local_address="127.0.0.1",
        local_port=5000,
        remote_address="127.0.0.1",
        remote_port=443,
        status="ESTABLISHED",
        protocol="tcp",
    )

    result = connection.to_dict()

    assert result["local_address"] == "127.0.0.1"
    assert result["local_port"] == 5000
    assert result["remote_address"] == "127.0.0.1"
    assert result["remote_port"] == 443
    assert result["status"] == "ESTABLISHED"
    assert result["protocol"] == "tcp"


def test_network_telemetry_serializes_connections(fake_host):
    connection = NetworkConnection(
        local_address="127.0.0.1",
        local_port=5000,
        remote_address=None,
        remote_port=None,
        status="LISTEN",
        protocol="tcp",
    )

    telemetry = NetworkTelemetry(
        timestamp=datetime.now(),
        connection_count=1,
        tcp_connection_count=1,
        udp_connection_count=0,
        listening_port_count=1,
        connections=(connection,),
    )

    result = telemetry.to_dict()

    assert result["connection_count"] == 1
    assert result["tcp_connection_count"] == 1
    assert result["udp_connection_count"] == 0
    assert result["listening_port_count"] == 1
    assert len(result["connections"]) == 1
    assert result["connections"][0]["protocol"] == "tcp"


def test_denied_network_is_unavailable(monkeypatch):
    import psutil
    import pytest

    from threatlens.features.network import extract_network_features

    def denied(kind):
        raise psutil.AccessDenied()

    monkeypatch.setattr(psutil, "net_connections", denied)
    data = collect_network_telemetry()
    assert not data.available
    with pytest.raises(ValueError, match="unavailable"):
        extract_network_features(data)
