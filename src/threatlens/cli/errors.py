"""Consistent operational failures without dumping telemetry or stack traces."""

import sqlite3
from functools import wraps

import typer


def handle_errors(command):
    @wraps(command)
    def wrapped(*args, **kwargs):
        try:
            return command(*args, **kwargs)
        except (OSError, sqlite3.Error, ValueError) as error:
            typer.echo(f"ThreatLens: {error}", err=True)
            raise typer.Exit(2) from None

    return wrapped
