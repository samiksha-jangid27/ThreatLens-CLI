from typer.testing import CliRunner

from threatlens.cli.app import app


runner = CliRunner()


def test_incidents_command_is_registered():
    result = runner.invoke(
        app,
        ["incidents"],
    )

    assert result.exit_code == 0


def test_investigate_command_is_registered():
    result = runner.invoke(
        app,
        ["investigate", "999999"],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()