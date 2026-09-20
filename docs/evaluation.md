# ThreatLens Evaluation

## Overview

ThreatLens includes a deterministic behavioral benchmark designed to validate the implemented detection pipeline under controlled scenarios.

The benchmark is intended primarily for regression testing and engineering validation.

It is **not** intended to represent real-world attack detection performance.

---

## Evaluation Metrics

The benchmark calculates the following metrics:

- Accuracy
- Precision
- Recall
- F1 Score
- False Positive Rate
- Detection Rate

### Accuracy

Measures the proportion of correct predictions across all evaluated scenarios.

```text
Accuracy = Correct Predictions / Total Predictions
```

### Precision

Measures how many detections classified as suspicious were actually suspicious within the benchmark scenarios.

```text
Precision = TP / (TP + FP)
```

### Recall

Measures how many of the configured anomalous scenarios were detected.

```text
Recall = TP / (TP + FN)
```

### F1 Score

Combines precision and recall into a single metric.

```text
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

### False Positive Rate

Measures the proportion of normal scenarios incorrectly classified as anomalous.

```text
FPR = FP / (FP + TN)
```

### Detection Rate

Represents the proportion of anomalous benchmark scenarios detected by the system.

---

## Benchmark Dataset

The current benchmark is deterministic and uses controlled synthetic observations.

Current evaluation configuration:

```text
Baseline observations: 5
Scenarios tested:      10
```

The benchmark contains examples representing normal behavior and controlled behavioral changes.

Examples include:

- normal behavior
- CPU spike
- memory spike
- process spike
- load spike
- multi-signal anomaly

---

## Current Benchmark Result

The current validated benchmark produced:

```text
Accuracy:             100.00%
Precision:            100.00%
Recall:               100.00%
F1 Score:             100.00%
False Positive Rate:    0.00%
Detection Rate:       100.00%
```

These results describe the behavior of the current implementation on the included controlled scenarios.

---

## Result Interpretation

The benchmark results must be interpreted within their scope.

```text
Controlled Synthetic Benchmark
              ≠
Real-World Security Evaluation
```

A perfect score on a deterministic synthetic benchmark does **not** establish:

- guaranteed compromise detection
- guaranteed low false-positive rates in production
- generalization across different operating environments
- effectiveness against unseen attack techniques
- effectiveness across different device types

The benchmark is therefore best treated as a repeatable regression test.

---

## Running the Benchmark

Run the benchmark through the CLI:

```bash
threatlens benchmark
```

Or using the Makefile:

```bash
make benchmark
```

For machine-readable output:

```bash
threatlens benchmark --json
```

---

## Regression Testing

The deterministic benchmark provides a stable reference point for future changes.

After modifying the detection pipeline, the benchmark can be rerun to determine whether the behavior of the implemented detector has changed.

The recommended validation sequence is:

```text
Code Change
     |
     v
Unit Tests
     |
     v
Benchmark
     |
     v
Compare Results
```

A benchmark result should always be considered together with the automated test suite.

---

## Automated Testing

ThreatLens also contains automated tests covering major components of the system, including:

- collectors
- ingestion
- feature extraction
- behavioral detection
- anomaly detection
- temporal detection
- signal correlation
- risk scoring
- incident storage
- CLI commands
- reporting
- evaluation

The current validated repository state contains:

```text
97 tests passing
```

Run the complete test suite with:

```bash
pytest -q
```

Or use:

```bash
make check
```

---

## Limitations of the Current Evaluation

The current benchmark has several limitations.

### Synthetic Data

The scenarios are controlled rather than collected from real compromised systems.

### Limited Scenario Diversity

The benchmark does not represent the full range of:

- operating environments
- workloads
- attack techniques
- network conditions
- process behaviors

### Limited Device Coverage

The current implementation focuses on Linux-oriented system, network, and process behavior.

It does not provide a complete evaluation across all firewall and router platforms.

### No Production Ground Truth

A production security evaluation requires reliable labels indicating whether an observed environment is benign or compromised.

Such representative ground-truth telemetry is outside the scope of the current benchmark.

---

## Recommended Real-World Evaluation

A future security evaluation should use representative labeled telemetry containing both:

```text
Benign Behavior
       +
Confirmed Compromised Behavior
```

The evaluation should ideally cover:

- multiple systems
- different workloads
- different network environments
- multiple attack techniques
- different observation windows
- normal operational changes

The same metrics can then be used to measure detection behavior against a more representative dataset.

---

## Evaluation Philosophy

ThreatLens evaluates its current implementation in two complementary ways:

```text
Automated Tests
      +
Deterministic Benchmark
      |
      v
Engineering Validation
```

These checks establish that the implemented components behave consistently under the repository's defined test and benchmark scenarios.

They do not replace real-world security validation.

---

## Summary

The current evaluation confirms that the implemented detector performs correctly on the included deterministic scenarios.

The current benchmark result is:

```text
Accuracy:             100.00%
Precision:            100.00%
Recall:               100.00%
F1 Score:             100.00%
False Positive Rate:    0.00%
Detection Rate:       100.00%
```

These results should be understood as **controlled benchmark results for the current implementation**, not as a claim of real-world security effectiveness.
