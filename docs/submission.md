# Submission guide

The project addresses the supplied NTRO 2023 software problem statement: explore AI/ML compromise detection that does not rely only on known Indicators of Compromise. Its present result is an explainable behavioral prototype with working CLI workflows, not a certified compromise detector.

## Evaluation criteria mapping

| Supplied criterion | Implemented evidence | Boundary to explain honestly |
| --- | --- | --- |
| Innovation and ruggedness | Per-source Isolation Forest and median/MAD, extreme-deviation fallback, source consensus, persistence, replay rejection, schema checks, atomic state and evidence retention | Existing algorithms combined in an application; no claim of a novel ML algorithm or resistance to privileged telemetry tampering |
| Utility across device types | Local host adapter; system/router/firewall/network schema; Zeek TSV adapter; separate baselines and four-device demonstration | Router/firewall JSON is an export integration path; no direct vendor polling or physical-device validation |
| Ease of deployment and reporting | Python package, CLI entry point, isolated configuration, offline inputs, Docker definition, SQLite, terminal/JSON/HTML, reproducible demo | Python and compatible dependencies required; Docker does not automatically see its host; native installers deferred |
| Minimize false alarms | Meaningful-deviation floors, missing-data handling, frozen training, multiple domains or repeated windows, episode grouping, hard benign benchmark cases | Legitimate correlated changes still alert; synthetic FPR is 20%, not a production estimate |

## Materials included

- Source under `src/`, tests under `tests/`, dependency metadata and lock, and CI configuration.
- README, architecture, detection method, threat model, telemetry contract, evaluation and validation record.
- Synthetic examples for four device profiles, generators and the end-to-end demo script.
- Formal editable Word report and PDF under `docs/submission/`.
- Beginner code guide and viva preparation in `docs/learning-guide.md`.
- Changelog, contribution instructions and security reporting guidance.

## Suggested demonstration sequence

1. Show `python -m threatlens --help` and explain that this is a Python CLI.
2. Explain normal behavioral training and why a known-malicious IP list is unnecessary.
3. Run `python scripts/demo.py --output demo-artifacts` in a fresh directory.
4. Show the normal and suspicious statuses for each profile, and the second-window alert for a sustained network anomaly.
5. Open the generated HTML report and show a feature's current value, trusted median, robust score and model result.
6. Run `threatlens status --json` using the demo's state directory if inspecting it manually.
7. Present the benchmark's confusion matrix, including its authorized-backup false alarm and stealth false negative.
8. Explain physical-device and real-compromise validation as remaining research, then show the tests and package build evidence.

To inspect the demo database manually, set `THREATLENS_DATA_DIR` to the demo's `state` subdirectory. The demo does not modify the default user database.

## Before handing in

Use the institution's required cover page, course name, roll number and supervisor details; these were not supplied and are not invented in the report. Include any required disclosure of AI-assisted development. Do not sign an originality declaration you cannot support. Read the learning guide and run the demo yourself so you can explain the implementation and its limits.

Submit source and report together. Do not include `.venv`, real telemetry, private databases, caches or credentials. The wheel and source archive are technical install artifacts; public distribution and licensing decisions can be handled separately after submission.

## Regenerate the editable report

```bash
python -m pip install ".[docs]"
python scripts/build_submission_report.py
```

The builder reads the checked-in benchmark, validation summary and architecture image. Export the resulting Word file to PDF using Word or LibreOffice and inspect the pages before submitting an updated report. Update validation evidence before regenerating it; a document generator does not rerun the underlying tests.
