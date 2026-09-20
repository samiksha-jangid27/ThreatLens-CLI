# ThreatLens

> **AI-powered behavioral threat detection CLI for detecting potential system compromise without relying solely on known Indicators of Compromise (IoCs).**

ThreatLens is a cybersecurity CLI that analyzes **system, network, and process behavior** to detect suspicious deviations from a learned behavioral baseline.

Instead of depending only on known malicious hashes, IP addresses, domains, or signatures, ThreatLens focuses on **what a machine normally does** and identifies significant behavioral changes that may warrant investigation.

---

## Overview

Traditional security detection often relies heavily on known Indicators of Compromise (IoCs).

That creates a limitation:

> What happens when the IoC is unknown?

ThreatLens explores a **non-IoC behavioral detection approach**.

It collects telemetry from a system, converts that telemetry into behavioral features, compares current behavior against historical observations, combines multiple anomaly signals, assigns a risk score, and explains the evidence behind the detection.

### Current scope

The current implementation focuses on:

- Linux system telemetry
- Network connection telemetry
- Process telemetry
- Behavioral baselines
- Statistical anomaly detection
- Isolation Forest anomaly detection
- Temporal anomaly detection
- Multi-signal correlation
- Risk scoring
- Explainability
- Incident storage
- Incident investigation
- JSON and HTML reporting
- Detection benchmarking
- Docker-based deployment
- CI validation

Future adapters can extend the same architecture to firewalls, routers, and other infrastructure devices.

---

# Problem Statement

Early detection of compromise is important for protecting critical information infrastructure.

A compromise may not always expose a known IoC immediately.

ThreatLens therefore focuses on **behavioral deviations** such as:

- unexpected CPU utilization
- abnormal memory usage
- sudden process-count changes
- unusual process behavior
- changes in listening ports
- unexpected network connections
- unusual remote endpoints
- changes in traffic-related behavioral features
- multiple correlated anomalies across different telemetry sources

The objective is not to declare every anomaly malicious.

Instead, ThreatLens attempts to identify **behavior that significantly deviates from the learned normal baseline and deserves investigation**.

---

# Key Idea

The core detection philosophy is:

```text
Known IoC
   ↓
Traditional detection

Unknown IoC
   ↓
Behavioral change
   ↓
Feature extraction
   ↓
Baseline comparison
   ↓
Multiple anomaly signals
   ↓
Correlation
   ↓
Risk score
   ↓
Investigation
```

---

# Architecture

```text
                 ┌─────────────────────┐
                 │      Telemetry      │
                 └──────────┬──────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
       System Data     Network Data     Process Data
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                  ┌──────────────────┐
                  │ Feature Extraction│
                  └────────┬─────────┘
                           ▼
                ┌──────────────────────┐
                │ Behavioral Baseline  │
                └──────────┬───────────┘
                           ▼
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   Isolation Forest   Temporal         Behavioral
      Detection       Detection        Deviation
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                  Network + Process
                      Analysis
                           │
                           ▼
                  Multi-Signal Correlation
                           │
                           ▼
                      Risk Scoring
                           │
                           ▼
                     Explainability
                           │
                           ▼
                       Incident
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Investigate     Explain        Report
                           │
                           ▼
                       Benchmark
```

---

# Detection Pipeline

ThreatLens processes telemetry through several stages.

## 1. Collection

The collectors gather:

### System telemetry

- CPU utilization
- memory utilization
- available memory
- load average
- process count
- uptime
- disk utilization

### Network telemetry

- total connections
- TCP connections
- UDP connections
- established connections
- listening ports
- local ports
- remote ports
- remote addresses

### Process telemetry

- process count
- process names
- users
- CPU usage
- memory usage
- process state
- parent process relationships

---

## 2. Normalization

Raw telemetry is converted into a consistent internal representation.

```text
Raw telemetry
      ↓
Validation
      ↓
Normalization
      ↓
Structured observation
```

This allows different collectors to feed the same detection pipeline.

---

## 3. Feature Extraction

Raw telemetry is transformed into behavioral features.

Examples include:

```text
System
├── cpu_percent
├── memory_percent
├── load_average_1m
├── process_count
└── disk_percent

Network
├── connection_count
├── established_connection_count
├── listening_port_count
├── unique_remote_addresses
└── unique_remote_ports

Process
├── total_processes
├── unique_process_names
├── unique_users
├── high_cpu_process_count
├── high_memory_process_count
├── root_process_count
└── process-state features
```

---

# Behavioral Baseline

ThreatLens learns what normal behavior looks like from historical observations.

The baseline is deliberately bounded so that old observations do not grow indefinitely.

```text
Historical observations
        ↓
Behavioral baseline
        ↓
Current observation
        ↓
Deviation analysis
```

Only observations considered normal are added back into the active baseline.

This prevents known suspicious observations from automatically becoming the new definition of "normal."

---

# Behavioral Deviation Detection

ThreatLens uses robust statistics to reduce sensitivity to unusual historical samples.

The behavioral detector uses:

- Median
- Median Absolute Deviation (MAD)
- robust deviation scoring
- minimum meaningful deviation thresholds

Conceptually:

```text
Current behavior
      ↓
Compare with baseline
      ↓
Median / MAD
      ↓
Deviation score
      ↓
Anomaly decision
```

This is designed to reduce false alarms caused by very small changes in features with extremely low historical variance.

---

# Machine Learning Detection

ThreatLens also uses **Isolation Forest** for unsupervised anomaly detection.

Isolation Forest attempts to identify observations that differ from the learned behavioral distribution.

```text
Normal historical behavior
          ↓
     Isolation Forest
          ↓
Current observation
          ↓
Anomaly score
```

The ML detector is not used as the only decision source.

Instead, it is one signal within a larger multi-signal detection architecture.

---

# Temporal Detection

Behavior can also be suspicious when it changes rapidly.

ThreatLens compares the current observation with the previous observation to identify sudden changes in:

- CPU
- memory
- load
- process count
- disk utilization
- network features
- process features

```text
Previous observation
        ↓
Current observation
        ↓
Calculate change
        ↓
Temporal anomaly signal
```

---

# Network Behavioral Detection

Network behavior is analyzed without depending exclusively on known malicious IPs or domains.

ThreatLens can examine behavioral changes in:

- connection counts
- established connections
- TCP/UDP activity
- listening ports
- local ports
- remote ports
- unique remote addresses

This allows the system to detect **unexpected network behavior even when no known IoC is available**.

---

# Process Behavioral Detection

Process telemetry provides another independent behavioral signal.

ThreatLens analyzes:

- total process count
- unique process names
- unique users
- CPU-heavy processes
- memory-heavy processes
- root-owned processes
- running processes
- sleeping processes
- stopped processes
- parent-process relationships

This helps identify unusual process-level behavior that may not be visible from aggregate CPU or memory metrics alone.

---

# Multi-Signal Correlation

A single anomaly does not necessarily indicate compromise.

For example:

```text
CPU spike
```

could simply mean a legitimate workload started.

ThreatLens therefore combines signals.

Example:

```text
Isolation Forest anomaly
        +
Network behavioral anomaly
        +
Process behavioral anomaly
        ↓
Multi-signal correlation
        ↓
Higher confidence for investigation
```

The goal is to reduce unnecessary alerts caused by isolated benign changes.

---

# Risk Scoring

ThreatLens converts triggered detection signals into a bounded risk score.

Current signal categories include:

```text
Isolation Forest
Temporal anomaly
Behavioral deviation
Network anomaly
Process anomaly
```

The result includes:

- risk score
- severity
- triggered signals
- individual contributions

Example:

```text
Risk Score: 75/100
Severity: HIGH

Signals:
- isolation_forest
- network_anomaly
- process_anomaly
```

Risk scoring is an investigation aid and does not by itself prove that a compromise occurred.

---

# Explainability

A detection system should answer:

> **Why was this incident flagged?**

ThreatLens therefore converts detection signals into human-readable evidence.

Example:

```text
ThreatLens Evidence

● Current system behavior was classified as anomalous
  by the Isolation Forest model.

● Network behavior deviates from the learned network baseline.

● Process behavior deviates from the learned process baseline.

Summary:
3 behavioral signals contributed to the risk assessment.
```

This allows an analyst to move from:

```text
"Something is anomalous."
```

to:

```text
"These behavioral signals changed."
```

---

# Incident Lifecycle

```text
Telemetry
    ↓
Detection
    ↓
Correlation
    ↓
Risk Score
    ↓
Incident Created
    ↓
Investigation
    ↓
Explanation
    ↓
Report
```

Incidents are stored locally using SQLite.

---

# CLI

## Show help

```bash
threatlens --help
```

Available commands:

```text
version
status
incidents
investigate
explain
report
benchmark
scan
```

---

## Run a scan

```bash
threatlens scan
```

The first runs collect baseline observations.

Once enough behavioral observations exist, ThreatLens begins multi-signal anomaly detection.

---

## List incidents

```bash
threatlens incidents
```

JSON output:

```bash
threatlens incidents --json
```

---

## Investigate an incident

```bash
threatlens investigate <incident-id>
```

Example:

```bash
threatlens investigate 1
```

This shows:

- incident ID
- risk score
- severity
- priority
- status
- triggered signals
- behavioral evidence
- recommendation

---

## Explain an incident

```bash
threatlens explain <incident-id>
```

Example:

```bash
threatlens explain 1
```

Machine-readable output:

```bash
threatlens explain 1 --json
```

---

# Reporting

ThreatLens supports multiple report formats.

## Terminal

```bash
threatlens report
```

## JSON

```bash
threatlens report --format json
```

Specify an output file:

```bash
threatlens report \
    --format json \
    --output ./threatlens-report.json
```

## HTML

```bash
threatlens report --format html
```

Specify an output file:

```bash
threatlens report \
    --format html \
    --output ./threatlens-report.html
```

The HTML report is standalone and can be opened directly in a browser.

---

# Evaluation

ThreatLens includes a deterministic behavioral benchmark.

Run:

```bash
threatlens benchmark
```

Or:

```bash
make benchmark
```

The benchmark reports:

- Accuracy
- Precision
- Recall
- F1 Score
- False Positive Rate
- Detection Rate

It also evaluates individual scenarios.

Current benchmark scenarios include examples such as:

```text
Normal behavior
CPU spike
Memory spike
Process spike
Load spike
Multi-signal spike
```

## Current benchmark result

The current controlled benchmark contains:

```text
10 scenarios
5 baseline observations
```

The current run produced:

```text
Accuracy:             100.00%
Precision:            100.00%
Recall:               100.00%
F1 Score:             100.00%
False Positive Rate:    0.00%
Detection Rate:       100.00%
```

### Important

These numbers are from **controlled synthetic benchmark scenarios**.

They should not be interpreted as evidence of 100% real-world attack detection performance.

A production evaluation would require representative labeled telemetry containing both:

- benign behavior
- confirmed compromised behavior

across multiple devices, workloads, attack techniques, and network environments.

---

# Testing

ThreatLens has an automated test suite covering:

- collectors
- schemas
- normalization
- validation
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

Run all tests:

```bash
pytest -q
```

Current repository state:

```text
97 tests passing
```

Compile the source:

```bash
python -m compileall src
```

Or run the complete local quality check:

```bash
make check
```

---

# Docker

ThreatLens can be packaged as a Docker image.

## Build

```bash
docker build -t threatlens .
```

## Run CLI help

```bash
docker run --rm threatlens --help
```

## Example

```bash
docker run --rm threatlens benchmark
```

### Container limitation

ThreatLens is designed to inspect system and network behavior.

A normal Docker container does not automatically have unrestricted access
to the host's process, network, and filesystem namespaces.

For host-level telemetry collection in a containerized deployment,
additional privileges, namespace configuration, mounts, or an agent-based
architecture may be required.

---

# CI

ThreatLens uses GitHub Actions for automated validation.

The CI pipeline performs:

```text
Checkout
   ↓
Python setup
   ↓
Install project
   ↓
Run tests
   ↓
Compile source
   ↓
Verify CLI
   ↓
Run benchmark
```

The goal is to catch regressions automatically on pushes and pull requests.

---

# Make Commands

Common development commands:

```bash
make install
make test
make compile
make check
make benchmark
make docker-build
make docker-help
```

---

# Installation

## Requirements

Recommended:

- Python 3.12+
- pip
- virtual environment
- Docker Desktop (optional)

The project supports Python:

```text
Python >= 3.11
```

---

## Local setup

Clone the repository:

```bash
git clone https://github.com/samiksha-jangid27/ThreatLens-CLI.git
cd ThreatLens-CLI
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install:

```bash
python -m pip install .
```

For development:

```bash
python -m pip install ".[dev]"
```

---

# Project Structure

```text
ThreatLens-CLI/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── datasets/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── architecture.md
│   ├── detection-methodology.md
│   ├── evaluation.md
│   └── threat-model.md
│
├── models/
│   └── artifacts/
│
├── scripts/
│
├── src/
│   └── threatlens/
│       │
│       ├── cli/
│       │   ├── app.py
│       │   └── commands/
│       │       ├── benchmark.py
│       │       ├── explain.py
│       │       ├── incidents.py
│       │       ├── investigate.py
│       │       ├── report.py
│       │       ├── scan.py
│       │       └── status.py
│       │
│       ├── collectors/
│       │   ├── network.py
│       │   ├── processes.py
│       │   └── system.py
│       │
│       ├── detection/
│       │   ├── baseline.py
│       │   ├── behavioral.py
│       │   ├── correlation.py
│       │   ├── engine.py
│       │   ├── investigation.py
│       │   ├── pipeline.py
│       │   ├── risk.py
│       │   └── temporal.py
│       │
│       ├── evaluation/
│       │   └── benchmark.py
│       │
│       ├── explainability/
│       │   └── explainer.py
│       │
│       ├── features/
│       │   ├── network.py
│       │   ├── network_temporal.py
│       │   ├── process.py
│       │   └── system.py
│       │
│       ├── ingestion/
│       │   ├── normalizer.py
│       │   ├── parser.py
│       │   └── validator.py
│       │
│       ├── models/
│       │   └── isolation_forest.py
│       │
│       ├── reporting/
│       │   ├── html.py
│       │   ├── json.py
│       │   └── terminal.py
│       │
│       ├── schema/
│       │   ├── network.py
│       │   ├── process.py
│       │   └── telemetry.py
│       │
│       └── storage/
│           ├── database.py
│           └── repositories.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── .dockerignore
├── .gitignore
├── CHANGELOG.md
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
└── pyproject.toml
```

---

# Design Principles

## 1. Behavioral first

Detection should not depend exclusively on known IoCs.

## 2. Multiple signals

One anomaly is not automatically treated as compromise.

## 3. Explainable results

Detections should provide evidence that analysts can understand.

## 4. False-alarm awareness

Behavioral systems must account for legitimate workload changes.

## 5. Local-first deployment

The CLI is designed to operate without requiring a mandatory cloud backend.

## 6. Modular architecture

Collectors, features, detection engines, storage, and reporting are separated so additional device types can be added later.

---

# Security Considerations

ThreatLens is a defensive detection and monitoring tool.

It should be deployed with appropriate permissions and according to the security policy of the environment being monitored.

Telemetry may contain sensitive operational information such as:

- process names
- usernames
- network endpoints
- system utilization
- timestamps

Access to generated telemetry and incident reports should therefore be controlled appropriately.

---

# Limitations

The current version is an MVP focused primarily on Linux endpoint behavior.

Current limitations include:

- no complete native adapter for every firewall platform
- no complete native adapter for every router platform
- limited authentication-event analysis
- limited long-term model persistence
- synthetic benchmark scenarios
- no claim of guaranteed compromise detection
- no claim that every anomaly is malicious

A behavioral anomaly should be treated as a signal requiring investigation, not automatic proof of compromise.

---

# Future Work

Potential future improvements include:

### Infrastructure adapters

- firewall telemetry
- router telemetry
- network-device adapters
- authentication-event collectors

### Advanced modeling

- autoencoder-based anomaly detection
- sequence models
- temporal neural networks
- ensemble models
- adaptive baseline learning
- model calibration

### Detection improvements

- richer network-flow features
- user behavior modeling
- parent-child process graphs
- event sequencing
- longer observation windows
- contextual anomaly detection

### Deployment

- centralized agent architecture
- distributed telemetry collection
- security dashboard
- REST API
- alert integrations

---

# Development Roadmap

```text
Phase 1
├── System telemetry
├── Feature extraction
└── Behavioral baseline

Phase 2
├── Network telemetry
├── Process telemetry
└── Temporal analysis

Phase 3
├── Isolation Forest
├── Behavioral deviation
├── Signal correlation
└── Risk scoring

Phase 4
├── Incident storage
├── Investigation
├── Explainability
└── Reporting

Phase 5
├── Benchmarking
├── Docker
├── CI
└── Documentation

Future
├── Firewall adapters
├── Router adapters
├── Advanced ML
└── Centralized deployment
```

---

# Contributing

Contributions should preserve the modular architecture and include tests for new functionality.

Recommended workflow:

```bash
git checkout -b feature/<name>
```

Make changes and run:

```bash
make check
```

Then commit using conventional commit style:

```bash
git commit -m "feat: add new capability"
```

---

# License

This project is distributed under the license included in:

```text
LICENSE
```

---

# Project Status

**Version:** `0.1.0`

**Status:** MVP / active development

ThreatLens currently provides an end-to-end behavioral detection workflow:

```text
Collect
   ↓
Normalize
   ↓
Extract Features
   ↓
Learn Baseline
   ↓
Detect Anomalies
   ↓
Correlate Signals
   ↓
Calculate Risk
   ↓
Explain Evidence
   ↓
Create Incident
   ↓
Investigate
   ↓
Report
   ↓
Benchmark
```

---

# Repository

GitHub:

https://github.com/samiksha-jangid27/ThreatLens-CLI