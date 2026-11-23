"""Exercise installed CLI commands using isolated, synthetic four-device evidence."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from generate_examples import generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="A new output directory")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Output directory must be new or empty; existing reports are preserved")
    output.mkdir(parents=True, exist_ok=True)
    generate(output / "fixtures")
    environment = dict(os.environ, THREATLENS_DATA_DIR=str(output / "state"))

    def run(*arguments):
        process = subprocess.run(
            [sys.executable, "-m", "threatlens", *arguments],
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        return process.stdout

    summary = {}
    for kind in ("system", "router", "firewall", "network"):
        run("learn", "--input", str(output / "fixtures" / f"{kind}-baseline.json"))
        normal = json.loads(
            run("scan", "--input", str(output / "fixtures" / f"{kind}-normal.json"), "--json")
        )
        assert not normal["results"][0]["is_suspicious"]
        suspicious = json.loads(
            run("scan", "--input", str(output / "fixtures" / f"{kind}-suspicious.json"), "--json")
        )
        assert suspicious["results"][-1]["is_suspicious"]
        (output / f"{kind}-scan.json").write_text(
            json.dumps(suspicious, indent=2), encoding="utf-8"
        )
        summary[kind] = {
            "normal_status": normal["results"][0]["status"],
            "suspicious_status": suspicious["results"][-1]["status"],
            "incident_id": suspicious["results"][-1]["incident_id"],
        }
    run("report", "--format", "json", "--output", str(output / "incidents.json"))
    run("report", "--format", "html", "--output", str(output / "incidents.html"))
    (output / "benchmark.json").write_text(run("benchmark", "--json"), encoding="utf-8")
    (output / "demo-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
