import typer
from threatlens.cli.commands.report import (
    report,
)

from threatlens.cli.commands.explain import (
    explain,
)
from threatlens.cli.commands.incidents import (
    incidents,
)
from threatlens.cli.commands.investigate import (
    investigate,
)
from threatlens.cli.commands.scan import (
    scan,
)
from threatlens.cli.commands.status import (
    status,
)
from threatlens.cli.commands.version import (
    version,
)


app = typer.Typer(
    name="threatlens",
    help="AI-powered behavioral threat detection CLI.",
)


app.command()(version)
app.command()(status)
app.command()(incidents)
app.command()(investigate)
app.command()(explain)
app.command()(report)
app.command()(scan)

if __name__ == "__main__":
    app()