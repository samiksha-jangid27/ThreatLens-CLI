# Contributing

Use Python 3.11+ and install `.[dev]`, or use `uv sync --frozen --extra dev`. Keep changes focused and explain the behavioral problem they solve. Add regression tests for detection, parser, persistence or privacy changes. Use synthetic data in tests and never commit real telemetry or secrets.

Run `make check`, `python -m threatlens benchmark --json`, `python scripts/demo.py --output demo-artifacts`, and `python -m build`. The demo output directory must be new or empty. Test the built wheel from outside the source tree when changing packaging. A Docker definition is not proof that host telemetry is visible from a container.

If changing dependencies, regenerate `uv.lock` and run `pip-audit` against the environment used for validation. The lock is the exact dependency workflow; pip installation uses the supported version ranges. If changing feature meaning, update the contract, examples, tests, documentation and algorithm version as appropriate. Do not silently migrate a device to different units or a new profile.

Document evaluation data provenance, split strategy, class counts and limitations. Do not replace security validation with code coverage or promote synthetic accuracy as real-world attack detection effectiveness. Changes should preserve explicit baseline trust and saved evidence.

The existing all-rights-reserved license remains in effect. Any change to redistribution rights is the owner's decision.
