import pytest

from threatlens.ingestion.zeek import convert_zeek

HEADER = "#separator \\x09\n#fields\tts\tid.orig_h\tid.resp_h\tid.orig_p\tid.resp_p\tproto\torig_bytes\tresp_bytes\n"
ROW = "1767225600\t192.0.2.1\t198.51.100.2\t43210\t443\ttcp\t100\t200\n"


def test_zeek_aggregation_uses_behavior_not_endpoint_identity(tmp_path):
    path = tmp_path / "conn.log"
    path.write_text(HEADER + ROW + ROW.replace("1767225600", "1767225610"))
    document = convert_zeek(path, "lab-sensor")
    features = document["observations"][0]["sources"]["network"]
    assert features["connection_count"] == 2
    assert features["bytes_out"] == 200
    assert features["unique_remote_addresses"] == 1
    assert "192.0.2.1" not in str(document)


@pytest.mark.parametrize(
    "row",
    [
        ROW.replace("100\t200", "-\t200"),
        ROW.replace("43210", "99999"),
        ROW.replace("192.0.2.1", "invalid"),
        ROW.replace("1767225600", "nan"),
    ],
)
def test_zeek_invalid_records_are_not_silently_zero_filled(tmp_path, row):
    path = tmp_path / "bad.log"
    path.write_text(HEADER + row)
    with pytest.raises(ValueError, match="line"):
        convert_zeek(path, "lab")


def test_zeek_requires_header(tmp_path):
    path = tmp_path / "bad.log"
    path.write_text(ROW)
    with pytest.raises(ValueError, match="header"):
        convert_zeek(path, "lab")
