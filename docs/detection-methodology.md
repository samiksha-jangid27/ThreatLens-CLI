# ThreatLens Detection Methodology

## Objective

ThreatLens detects behavioral deviations that may indicate suspicious activity without depending exclusively on known Indicators of Compromise (IoCs).

The system combines statistical analysis, machine-learning anomaly detection, temporal changes, network behavior, process behavior, and multi-signal correlation.

An anomaly is treated as evidence for investigation, not as automatic proof of compromise.

## 1. Behavioral Baseline

ThreatLens first establishes a baseline from historical observations considered normal.

```text
Historical Observations
          |
          v
   Behavioral Baseline
          |
          v
   Current Observation
          |
          v
   Deviation Analysis
```

The baseline provides the reference range for expected system behavior.

Suspicious observations are not automatically added back into the normal baseline.

## 2. Feature Extraction

Raw telemetry is converted into behavioral features.

### System Features

```text
CPU utilization
Memory utilization
Available memory
Load average
Process count
Disk utilization
```

### Network Features

```text
Connection count
TCP connections
UDP connections
Established connections
Listening connections
Unique local ports
Unique remote ports
Unique remote addresses
```

### Process Features

```text
Total processes
Unique process names
Unique users
High-CPU processes
High-memory processes
Root processes
Running processes
Sleeping processes
Stopped processes
Parent-process relationships
Average CPU usage
Average memory usage
```

## 3. Isolation Forest

ThreatLens uses Isolation Forest as an unsupervised anomaly detector.

The model learns the distribution of historical system behavior and identifies observations that differ from that distribution.

```text
Historical Features
        |
        v
   Isolation Forest
        |
        v
Current Observation
        |
        v
Anomaly Signal
```

Isolation Forest is one signal within the complete detection pipeline and is not treated as a standalone compromise decision.

## 4. Temporal Detection

ThreatLens also examines how quickly system behavior changes.

The current observation is compared with the previous observation.

```text
Previous Observation
        |
        v
Current Observation
        |
        v
Calculate Change
        |
        v
Temporal Anomaly
```

Temporal analysis can detect sudden changes in:

- CPU
- memory
- load
- process count
- disk utilization
- network behavior
- process behavior

## 5. Behavioral Deviation

ThreatLens uses robust statistical methods to compare current behavior with the learned baseline.

The behavioral detector uses:

- Median
- Median Absolute Deviation (MAD)
- Deviation scores
- Minimum meaningful deviation thresholds

```text
Baseline
   |
   v
Median + MAD
   |
   v
Current Value
   |
   v
Deviation Score
   |
   v
Anomaly Decision
```

Median and MAD reduce sensitivity to extreme historical observations.

Minimum deviation thresholds help prevent insignificant changes in low-variance features from producing unnecessary alerts.

## 6. Network Behavioral Detection

Network behavior is analyzed independently from known malicious indicators.

ThreatLens compares current network characteristics against the learned network baseline.

```text
Historical Network Behavior
            |
            v
      Network Baseline
            |
            v
    Current Network State
            |
            v
      Network Deviation
```

Relevant signals include:

- connection counts
- established connections
- TCP/UDP activity
- listening behavior
- local ports
- remote ports
- remote addresses

## 7. Process Behavioral Detection

Process behavior provides another independent detection signal.

ThreatLens compares current process characteristics with historical process behavior.

```text
Historical Process Behavior
            |
            v
      Process Baseline
            |
            v
     Current Processes
            |
            v
     Process Deviation
```

Relevant signals include:

- process counts
- process names
- process users
- CPU-heavy processes
- memory-heavy processes
- root processes
- process states
- parent-process relationships

## 8. Multi-Signal Correlation

ThreatLens does not rely on a single anomaly whenever possible.

For example:

```text
Isolation Forest Anomaly
          +
Network Anomaly
          +
Process Anomaly
          |
          v
   Correlated Evidence
```

The correlation layer combines detection signals to provide broader context and reduce dependence on isolated anomalies.

## 9. Risk Scoring

Triggered detection signals are converted into a bounded risk score.

The assessment can include:

```text
Isolation Forest
Temporal Anomaly
Behavioral Deviation
Network Anomaly
Process Anomaly
```

The result includes information such as:

- risk score
- severity
- triggered signals

The score is intended to prioritize investigation and does not by itself prove compromise.

## 10. Explainability

ThreatLens converts detection results into human-readable evidence.

```text
Detection Signals
        |
        v
  Explainability
        |
        v
 Behavioral Evidence
```

The explanation can identify which types of behavior contributed to the detection.

## 11. Incident Creation

When the combined detection result is considered suspicious, ThreatLens can create an incident.

```text
Telemetry
    |
    v
Detection
    |
    v
Correlation
    |
    v
Risk Scoring
    |
    v
Incident
```

Incidents are stored locally using SQLite.

## 12. False-Alarm Reduction

Legitimate activity can cause behavioral deviations.

Examples include:

- software updates
- builds
- backups
- deployments
- scheduled maintenance
- temporary workload spikes

ThreatLens reduces reliance on individual anomalies by using:

- historical baselines
- robust statistics
- multiple detection signals
- correlation
- risk scoring
- learning only from non-suspicious observations

These mechanisms can reduce unnecessary alerts but cannot eliminate false positives completely.

## 13. Complete Detection Flow

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
Feature Extraction
      |
      v
Behavioral Baseline
      |
      +------------------+
      |                  |
      v                  v
Isolation Forest    Temporal Analysis
      |                  |
      +--------+---------+
               |
               v
       Behavioral Deviation
               |
               v
      Network + Process
          Detection
               |
               v
      Signal Correlation
               |
               v
         Risk Scoring
               |
               v
        Explainability
               |
               v
          Incident
```

## Detection Principle

The core principle of ThreatLens is:

```text
Behavioral Change
        +
Multiple Signals
        +
Context
        |
        v
Evidence for Investigation
```

rather than:

```text
Single Anomaly
        |
        v
Confirmed Compromise
```

The system is therefore designed to support early behavioral detection and investigation when known IoCs may be unavailable.