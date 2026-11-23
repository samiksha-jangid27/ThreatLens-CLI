import os

import pytest

from threatlens.storage.files import write_private_text


def test_output_is_private_and_existing_file_preserved(tmp_path):
    path = tmp_path / "report.json"
    write_private_text(path, "first")
    with pytest.raises(FileExistsError):
        write_private_text(path, "replacement")
    assert path.read_text() == "first"
    if os.name == "posix":
        assert path.stat().st_mode & 0o077 == 0


def test_output_refuses_symlink(tmp_path):
    original, link = tmp_path / "original", tmp_path / "link"
    original.write_text("private")
    link.symlink_to(original)
    with pytest.raises(FileExistsError):
        write_private_text(link, "overwrite")
    assert original.read_text() == "private"
