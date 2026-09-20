from threatlens.features.network import extract_network_features


def sample_network_data():
    return {
        "timestamp": "2026-09-20T12:00:00+00:00",
        "connection_count": 5,
        "tcp_connection_count": 4,
        "udp_connection_count": 1,
        "listening_port_count": 2,
        "connections": [
            {
                "local_address": "192.168.1.10",
                "local_port": 50000,
                "remote_address": "8.8.8.8",
                "remote_port": 443,
                "status": "ESTABLISHED",
                "protocol": "tcp",
            },
            {
                "local_address": "192.168.1.10",
                "local_port": 50001,
                "remote_address": "8.8.8.8",
                "remote_port": 443,
                "status": "ESTABLISHED",
                "protocol": "tcp",
            },
            {
                "local_address": "192.168.1.10",
                "local_port": 50002,
                "remote_address": "1.1.1.1",
                "remote_port": 443,
                "status": "ESTABLISHED",
                "protocol": "tcp",
            },
            {
                "local_address": "0.0.0.0",
                "local_port": 22,
                "remote_address": None,
                "remote_port": None,
                "status": "LISTEN",
                "protocol": "tcp",
            },
            {
                "local_address": "0.0.0.0",
                "local_port": 53,
                "remote_address": None,
                "remote_port": None,
                "status": "LISTEN",
                "protocol": "udp",
            },
        ],
    }


def test_extracts_network_features():
    features = extract_network_features(
        sample_network_data()
    )

    assert features["connection_count"] == 5.0
    assert features["tcp_connection_count"] == 4.0
    assert features["udp_connection_count"] == 1.0
    assert features["established_connection_count"] == 3.0
    assert features["listening_connection_count"] == 2.0
    assert features["unique_remote_addresses"] == 2.0
    assert features["unique_remote_ports"] == 1.0
    assert features["unique_local_ports"] == 5.0
    assert features["listening_port_count"] == 2.0


def test_empty_network_data():
    features = extract_network_features(
        {
            "connections": [],
        }
    )

    assert features == {
        "connection_count": 0.0,
        "tcp_connection_count": 0.0,
        "udp_connection_count": 0.0,
        "established_connection_count": 0.0,
        "listening_connection_count": 0.0,
        "unique_remote_addresses": 0.0,
        "unique_remote_ports": 0.0,
        "unique_local_ports": 0.0,
        "listening_port_count": 0.0,
    }


def test_missing_connections_are_handled():
    features = extract_network_features({})

    assert features["connection_count"] == 0.0
    assert features["unique_remote_addresses"] == 0.0
    assert features["listening_port_count"] == 0.0
