# Validation record

Recorded on 23 November 2026 for ThreatLens 0.2.0. This record separates observed engineering checks from security-effectiveness claims. The original GitHub revision reviewed was `800174c`.

| Check | Observed outcome |
| --- | --- |
| Local tests | 153 passed on macOS arm64, Python 3.14.3 |
| Coverage | 82.3% combined statement/branch coverage under pytest-cov |
| Lint and formatting | Ruff checks passed for source, tests and scripts |
| Compilation | Source compiled successfully |
| Dependency consistency | `pip check` passed |
| Dependency audit | No known vulnerabilities after upgrading the isolated environment's pip to 26.3 |
| Wheel and source archive | Both built using isolated build dependencies |
| Installed CLI | Version and help worked from the installed wheel, including isolated Python mode |
| Real local collection | Installed CLI exported one aggregate system observation successfully |
| Four-device demo | Trusted learning, benign checks, suspicious checks and JSON/HTML reports completed |
| Synthetic evaluation | 32 scenarios; TP 8, TN 16, FP 4, FN 4 |
| GitHub CI | Six OS/Python combinations and the package job passed in the linked run |
| Docker runtime | Not verified locally because the daemon was stopped |
| Physical router/firewall or confirmed compromise | Not tested; imports and synthetic profiles validated |

The cross-platform [GitHub run](https://github.com/samiksha-jangid27/ThreatLens-CLI/actions/runs/45190502068) assessed commit `8cc370e`. It passed Linux, macOS and Windows on Python 3.11 and 3.14, plus wheel/source packaging and installed-entry-point checks. Later regression and documentation changes also receive CI on direct pushes to `main`; consult the latest run for exact revision status. Scheduled vulnerability audits replace automatic dependency-update PR creation.

Reproduction commands:

```bash
python -m pip install ".[dev]"
python -m pytest -q --cov=threatlens --cov-report=term
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m compileall -q src
python -m pip check
python -m pip_audit --progress-spinner off
python -m threatlens benchmark --json
python scripts/demo.py --output demo-artifacts
python -m build
```

The developer's source tree and its installed wheel are distinct. After changes, rebuild and reinstall a wheel before checking installed behavior outside the checkout. The test configuration imports source modules explicitly and isolates monitoring state from the user's default directory.

`docs/submission/benchmark.json` contains the scenario outputs and ablation metrics. `docs/submission/validation.json` contains a concise machine-readable summary. The formal report was rendered and all eight pages visually inspected. Real host telemetry and private SQLite state are intentionally absent from the submission.

The perfect score from the original ten-scenario statistical component benchmark is not used as evidence of overall security performance. An alert is not confirmation of compromise, and a quiet or degraded scan is not evidence of safety.
