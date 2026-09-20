# ThreatLens Architecture

## Overview

ThreatLens is a CLI-based behavioral threat detection system designed to identify significant deviations from normal system behavior without relying only on known IoCs.

Current telemetry sources:

- System
- Network
- Process

## High-Level Architecture

```text
System / Network / Process Telemetry
                  |
                  v
        Validation / Normalization
                  |
                  v
          Feature Extraction
                  |
                  v
        Behavioral Baseline
                  |
        +---------+---------+
        |         |         |
        v         v         v
   Isolation   Temporal  Behavioral
    Forest     Detection  Deviation
        |         |         |
        +---------+---------+
                  |
                  v
       Network / Process Analysis
                  |
                  v
        Multi-Signal Correlation
                  |
                  v
             Risk Scoring
                  |
                  v
           Explainability
                  |
                  v
          Incident Storage
                  |
          +-------+-------+
          |               |
          v               v
     Investigation     Reporting
```

## Architectural Layers

### Collectors

Collect telemetry from the host.

```text
collectors/
├── system.py
├── network.py
└── processes.py
```

### Schema

Provides structured telemetry representations.

```text
schema/
├── telemetry.py
├── network.py
└── process.py
```

### Ingestion

Validates and normalizes collected telemetry.

```text
ingestion/
├── normalizer.py
└── validator.py
```

```text
Raw Telemetry
      |
      v
Validation
      |
      v
Normalization
      |
      v
Structured Observation
```

### Features

Converts telemetry into behavioral features.

```text
features/
├── system.py
├── network.py
├── network_temporal.py
├── process.py
└── temporal.py
```

### Detection

ThreatLens uses multiple detection signals:

```text
Isolation Forest
       +
Temporal Detection
       +
Behavioral Deviation
       +
Network Detection
       +
Process Detection
```

### Correlation

Combines multiple detection signals before risk assessment.

```text
Detection Signals
       |
       v
Signal Correlation
       |
       v
Combined Evidence
```

### Risk Scoring

Triggered signals are converted into a bounded risk score and severity level.

The score is an investigation aid, not proof of compromise.

### Explainability

Converts detection signals into human-readable behavioral evidence.

```text
Detection
   |
   v
Explainability
   |
   v
Evidence
```

### Storage

Suspicious detections are stored locally using SQLite.

```text
storage/
├── database.py
└── repositories.py
```

### Reporting

ThreatLens supports:

- Terminal reports
- JSON reports
- HTML reports

## Detection Flow

```text
Collect
   |
   v
Normalize
   |
   v
Extract Features
   |
   v
Compare with Baseline
   |
   v
Detect Anomalies
   |
   v
Correlate Signals
   |
   v
Calculate Risk
   |
   v
Explain Evidence
   |
   v
Create Incident
   |
   v
Investigate / Report
```

## CLI Flow

```text
threatlens scan
      |
      v
Detection + Correlation
      |
      v
Risk Assessment
      |
      v
Incident
      |
      +----> threatlens incidents
      |
      +----> threatlens investigate <id>
      |
      +----> threatlens explain <id>
      |
      +----> threatlens report
```

## Design Goal

ThreatLens keeps collection, feature extraction, detection, storage, and reporting modular so future capabilities can be added without rewriting the core detection pipeline.