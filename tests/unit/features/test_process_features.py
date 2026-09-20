from threatlens.features.process import extract_process_features


def sample_process_data():
    return {
        "timestamp": "2026-09-20T12:00:00+00:00",
        "process_count": 4,
        "processes": [
            {
                "pid": 100,
                "name": "python",
                "username": "samiksha",
                "cpu_percent": 10.0,
                "memory_percent": 2.0,
                "status": "running",
                "parent_pid": 1,
            },
            {
                "pid": 101,
                "name": "chrome",
                "username": "samiksha",
                "cpu_percent": 60.0,
                "memory_percent": 12.0,
                "status": "running",
                "parent_pid": 1,
            },
            {
                "pid": 102,
                "name": "python",
                "username": "root",
                "cpu_percent": 70.0,
                "memory_percent": 4.0,
                "status": "running",
                "parent_pid": 1,
            },
            {
                "pid": 103,
                "name": "nginx",
                "username": "root",
                "cpu_percent": 5.0,
                "memory_percent": 15.0,
                "status": "running",
                "parent_pid": 1,
            },
        ],
    }


def test_extracts_process_features():
    features = extract_process_features(
        sample_process_data()
    )

    assert features["total_processes"] == 4.0
    assert features["unique_process_names"] == 3.0
    assert features["unique_users"] == 2.0
    assert features["high_cpu_process_count"] == 2.0
    assert features["high_memory_process_count"] == 2.0
    assert features["root_process_count"] == 2.0


def test_custom_thresholds():
    features = extract_process_features(
        sample_process_data(),
        cpu_threshold=65.0,
        memory_threshold=14.0,
    )

    assert features["high_cpu_process_count"] == 1.0
    assert features["high_memory_process_count"] == 1.0


def test_empty_process_data():
    features = extract_process_features(
        {
            "processes": [],
        }
    )

    assert features == {
        "total_processes": 0.0,
        "unique_process_names": 0.0,
        "unique_users": 0.0,
        "high_cpu_process_count": 0.0,
        "high_memory_process_count": 0.0,
        "root_process_count": 0.0,
        "running_process_count": 0.0,
        "sleeping_process_count": 0.0,
        "stopped_process_count": 0.0,
        "unique_parent_processes": 0.0,
        "average_cpu_percent": 0.0,
        "average_memory_percent": 0.0,
    }


def test_missing_process_list():
    features = extract_process_features({})

    assert features["total_processes"] == 0.0
    assert features["unique_process_names"] == 0.0
    assert features["unique_users"] == 0.0
