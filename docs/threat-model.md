# ThreatLens Threat Model

## Scope

ThreatLens is a defensive behavioral threat detection and monitoring system.

The current implementation focuses on Linux-oriented:

- System telemetry
- Network telemetry
- Process telemetry

The goal is to identify behavioral deviations that may require security investigation, including cases where a known Indicator of Compromise (IoC) is unavailable.

---

## Assets Observed

ThreatLens may process operational information such as:

- CPU utilization
- Memory utilization
- System load
- Process metadata
- Process names
- Process users
- Process relationships
- Network connection metadata
- Local ports
- Remote ports
- Remote addresses
- Timestamps
- Behavioral baselines
- Detection results
- Incident records

Some of this information may be sensitive and should be protected accordingly.

---

## Threat Detection Objective

ThreatLens is designed to identify behavioral patterns that differ significantly from established normal behavior.

Examples include:

- Unusual resource consumption
- Unexpected process activity
- Unusual process counts
- Unexpected network connections
- Abnormal listening-port behavior
- Unusual remote endpoints
- Simultaneous changes across multiple telemetry sources

The system focuses on behavioral evidence rather than relying exclusively on known malicious hashes, addresses, domains, or signatures.

---

## Detection Assumption

ThreatLens assumes that historical observations can provide a useful representation of normal system behavior.

The detection model is:

```text
Normal Historical Behavior
          |
          v
   Behavioral Baseline
          |
          v
 Current System Behavior
          |
          v
   Behavioral Deviation
          |
          v
   Detection Evidence
          |
          v
      Investigation
```

A detected deviation is treated as an anomaly requiring investigation and is not automatically treated as confirmed compromise.

---

## Threat Sources

The system is designed to provide behavioral visibility into activity such as:

### System-Level Changes

```text
Unexpected CPU usage
Unexpected memory usage
Abnormal system load
Sudden process-count changes
Unusual disk utilization
```

### Process-Level Changes

```text
Unexpected processes
Unusual process counts
Unusual process resource usage
Unexpected privileged processes
Changes in process relationships
```

### Network-Level Changes

```text
Unexpected connections
Unusual connection counts
Unexpected remote addresses
Unusual remote ports
Unexpected listening behavior
Changes in TCP/UDP activity
```

---

## False Positives

Legitimate activity may produce behavioral deviations.

Examples include:

- Software updates
- Software builds
- Backups
- Deployments
- Scheduled maintenance
- High user workloads
- Temporary resource-intensive operations
- Normal changes in network activity

ThreatLens therefore avoids relying exclusively on a single anomaly.

Instead, it uses:

- Historical baselines
- Robust statistical analysis
- Temporal analysis
- Network analysis
- Process analysis
- Multiple detection signals
- Signal correlation
- Risk scoring

These mechanisms are intended to reduce unnecessary alerts but cannot eliminate false positives completely.

---

## False Negatives

Behavioral detection can fail to identify a compromise when malicious behavior remains close to normal behavior.

Potential situations include:

- Malicious activity closely resembles normal behavior
- Relevant telemetry is unavailable
- The observation window is too short
- The relevant behavior is not represented by collected features
- The attacker deliberately operates within the learned behavioral range
- The baseline does not adequately represent the environment

Therefore, absence of an alert does not prove that a system is uncompromised.

---

## Trust Boundaries

The main data flow is:

```text
Host
 |
 v
Telemetry Collectors
 |
 v
Validation / Normalization
 |
 v
Feature Extraction
 |
 v
Detection Pipeline
 |
 v
Risk / Explainability
 |
 v
SQLite Incident Storage
 |
 v
Reports / Investigation
```

The boundaries that require particular attention are:

1. Host telemetry entering the ThreatLens pipeline.
2. Detection data being written to local storage.
3. Incident information being exposed through reports.
4. Reports being accessed or transferred outside the monitored host.

---

## Data Protection Considerations

ThreatLens may expose operational information through telemetry and reports.

Sensitive information may include:

- Usernames
- Process names
- Network endpoints
- Port information
- System utilization
- Timestamps
- Incident details

Access to the ThreatLens database and generated reports should therefore be restricted according to the security requirements of the deployment environment.

---

## Permissions

ThreatLens should run with only the permissions required to collect the telemetry necessary for its detection workflow.

The deployment should follow the security policy of the monitored environment.

Excessive privileges should not be granted unless they are required for a specific telemetry source.

---

## Security-Relevant Outputs

ThreatLens may produce:

- Anomaly signals
- Risk scores
- Severity levels
- Triggered detection signals
- Behavioral evidence
- Incident records
- JSON reports
- HTML reports
- Terminal reports

These outputs should be treated as security-relevant information.

---

## ThreatLens Response Model

ThreatLens follows an evidence-oriented workflow:

```text
Behavioral Deviation
        |
        v
Detection Signal
        |
        v
Signal Correlation
        |
        v
Risk Assessment
        |
        v
Explainable Evidence
        |
        v
Investigation
```

The system is intentionally designed around investigation rather than automatically declaring every anomaly malicious.

---

## Non-Goals

The current implementation does not attempt to:

- Guarantee compromise detection
- Treat every anomaly as malicious
- Prove malicious intent from telemetry alone
- Replace a complete Endpoint Detection and Response platform
- Identify every malware family
- Provide complete support for every firewall platform
- Provide complete support for every router platform

These capabilities are outside the current MVP scope.

---

## Operational Principle

The core security principle is:

```text
Anomaly
   |
   v
Evidence
   |
   v
Investigation
```

rather than:

```text
Anomaly
   |
   v
Confirmed Compromise
```

A behavioral anomaly is therefore treated as a signal that deserves contextual investigation.

---

## Current Threat Model Boundary

The current ThreatLens threat model is primarily focused on detecting suspicious behavior through:

```text
System Behavior
       +
Network Behavior
       +
Process Behavior
       |
       v
Behavioral Detection
       |
       v
Correlated Evidence
```

The current implementation does not claim complete visibility into every possible attack technique or every infrastructure device.

Its purpose is to provide an additional behavioral detection layer that can operate even when a known IoC is not available.