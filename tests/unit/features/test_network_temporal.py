from threatlens.features.network_temporal import (
    calculate_delta,
    extract_network_temporal_features,
)


def test_calculate_delta():
    assert calculate_delta(100.0, 20.0) == 80.0
    assert calculate_delta(20.0, 100.0) == -80.0
    assert calculate_delta(50.0, 50.0) == 0.0


def test_extracts_network_temporal_features():
    previous = {
        "connection_count": 20,
        "tcp_connection_count": 15,
        "udp_connection_count": 5,
        "established_connection_count": 12,
        "listening_port_count": 3,
        "unique_remote_addresses": 5,
        "unique_remote_ports": 4,
    }

    current = {
        "connection_count": 150,
        "tcp_connection_count": 120,
        "udp_connection_count": 30,
        "established_connection_count": 100,
        "listening_port_count": 12,
        "unique_remote_addresses": 80,
        "unique_remote_ports": 15,
    }

    result = extract_network_temporal_features(
        current,
        previous,
    )

    assert result["connection_delta"] == 130.0
    assert result["tcp_connection_delta"] == 105.0
    assert result["udp_connection_delta"] == 25.0
    assert result["established_connection_delta"] == 88.0
    assert result["listening_port_delta"] == 9.0
    assert result["unique_remote_address_delta"] == 75.0
    assert result["unique_remote_port_delta"] == 11.0


def test_detects_negative_changes():
    previous = {
        "connection_count": 100,
        "tcp_connection_count": 80,
        "udp_connection_count": 20,
        "established_connection_count": 70,
        "listening_port_count": 10,
        "unique_remote_addresses": 50,
        "unique_remote_ports": 15,
    }

    current = {
        "connection_count": 20,
        "tcp_connection_count": 15,
        "udp_connection_count": 5,
        "established_connection_count": 10,
        "listening_port_count": 3,
        "unique_remote_addresses": 5,
        "unique_remote_ports": 4,
    }

    result = extract_network_temporal_features(
        current,
        previous,
    )

    assert result["connection_delta"] == -80.0
    assert result["tcp_connection_delta"] == -65.0
    assert result["udp_connection_delta"] == -15.0
    assert result["established_connection_delta"] == -60.0
    assert result["listening_port_delta"] == -7.0
    assert result["unique_remote_address_delta"] == -45.0
    assert result["unique_remote_port_delta"] == -11.0


def test_supports_nested_feature_dictionary():
    previous = {
        "features": {
            "connection_count": 10,
            "tcp_connection_count": 8,
            "udp_connection_count": 2,
            "established_connection_count": 6,
            "listening_port_count": 2,
            "unique_remote_addresses": 3,
            "unique_remote_ports": 2,
        }
    }

    current = {
        "features": {
            "connection_count": 30,
            "tcp_connection_count": 25,
            "udp_connection_count": 5,
            "established_connection_count": 20,
            "listening_port_count": 4,
            "unique_remote_addresses": 10,
            "unique_remote_ports": 5,
        }
    }

    result = extract_network_temporal_features(
        current,
        previous,
    )

    assert result["connection_delta"] == 20.0
    assert result["unique_remote_address_delta"] == 7.0
