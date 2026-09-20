# ThreatLens

AI-powered behavioral threat detection CLI for identifying potential
system and network compromise without relying solely on known
Indicators of Compromise (IoCs).

## Problem

ThreatLens aims to detect potential compromise of systems, firewalls,
routers, and networks using AI/ML-based behavioral analysis when known
Indicators of Compromise are unavailable.

## Current Status

🚧 Under active development.

## Planned Capabilities

- System telemetry collection
- Network telemetry analysis
- Behavioral anomaly detection
- ML-based compromise detection
- Deep learning-based anomaly detection
- Event correlation
- Risk scoring
- Explainable detections
- Incident reporting
- CLI-based deployment
- Firewall and router telemetry support

## Technology

- Python
- Typer
- Rich
- scikit-learn
- PyTorch
- Pandas
- NumPy

## Project Structure

```text
src/threatlens/
├── cli/
├── collectors/
├── ingestion/
├── schema/
├── features/
├── detection/
├── models/
├── explainability/
├── storage/
├── reporting/
└── config/