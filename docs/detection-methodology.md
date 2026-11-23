# Detection methodology

ThreatLens uses no threat-intelligence feed, malicious-address list, hash signature, or attack label in inference. It detects deviations from operator-approved normal behavior. The approach combines existing methods with source-level corroboration and temporal state; it does not claim to invent Isolation Forest or robust statistics.

## Trusted training

`learn` adds explicitly trusted observations for one device. Thirty observations are required to enable scanning and the latest 500 are retained. Profiles have identical source names, feature names and window durations. Learning refuses declared unavailable sources. Choose a deliberate narrower local profile with `--sources` if necessary. A ready flag means sufficient software input, not baseline quality.

`scan` never adds observations to training, including uncorrelated outliers. This avoids automatic poisoning through gradual or isolated suspicious samples. It also means legitimate workload drift requires reviewed relearning. Initial baseline trust and operator-supplied imports remain assumptions.

## Per-source ML

An Isolation Forest is trained for each source with a fixed random seed of 42 and contamination 0.05. Feature names are aligned deterministically. Contamination affects the learned score offset; it is not an estimated attack prevalence. The model reports its decision function, where a negative value is anomalous. There is no claim that raw scores from different devices are calibrated or comparable.

## Robust per-feature deviation

For baseline median m and median absolute deviation MAD:

```text
z = 0.6745 * (current - m) / MAD
```

The source's robust detector triggers when at least one feature has absolute z at least 3.5 and the absolute change is meaningful. The meaningful deviation floor is:

```text
max(1.0, 0.10 * abs(m), 0.000001)
```

When MAD is approximately zero, use `(current - m) / meaningful_floor` and require absolute change at least `3.5 * meaningful_floor`. This prevents tiny floating-point fluctuations from producing unlimited scores. Thresholds apply to feature units, so profile calibration is necessary before operational use.

NaN, infinity, negative metrics, booleans posing as numbers, unknown features and mismatched schemas are rejected on import. Missing source data is excluded from assessment and marked degraded, rather than imputed as zero. Uptime is not a behavioral model feature because normal elapsed time otherwise drifts continuously.

## Corroboration and time

A source is corroborated when robust deviation triggers and either:

1. Isolation Forest classifies its feature vector as anomalous; or
2. at least one absolute robust feature score reaches 6.

The extreme-deviation fallback matters when an Isolation Forest trained on nearly constant data cannot meaningfully rank an out-of-range sample. An ML-only outlier remains visible as `REVIEW` evidence.

A suspicious result requires either two corroborated source domains in one window or the same corroborated domain in at least two consecutive comparable windows. Comparable windows are separated by at least half the configured duration and no more than `max(300, 5 * window_seconds)` seconds. A long gap resets persistence. The previous observation always advances, even when suspicious; it is never substituted with the last normal training record.

Sources and algorithms can share underlying behavior, so corroboration is not statistical independence. Two changed sources may still reflect one benign backup job. Single-source transient events can be missed or delayed by design. Operators must examine context and independent evidence.

## Output decisions

- `INSUFFICIENT_BASELINE`: fewer than 30 trusted windows; detection was not performed.
- `NO_CORRELATED_ANOMALY`: no anomaly under the configured profile; no conclusion about compromise.
- `REVIEW`: one-off or uncorroborated evidence requiring context or another sample.
- `SUSPICIOUS`: cross-source or persistent corroboration warrants investigation.

Coverage is reported separately. A quiet result with missing sources is still degraded.

## Risk priority and episodes

Each corroborated source contributes 25 points, any model corroboration adds 10, and persistent evidence adds 20. The total is capped at 100. Uncorroborated review evidence receives 10 if no source contribution exists. Severity uses LOW below 30, MEDIUM from 30, HIGH from 60, and CRITICAL from 80. These are heuristic priorities, not compromise probabilities.

Continuing suspicious windows with the same source set reuse an incident ID and preserve original onset evidence. Recovery or a changed source set allows a new incident. Every scan still returns its current assessment. There is no automatic blocking, process termination or device reconfiguration.

Saved evidence includes feature values, baseline median, MAD, robust score, previous-value delta when available, ML score, source coverage, algorithm version, and the priority calculation. Incident explanation uses that saved evidence rather than re-running a model against a changed baseline.

## References

- [scikit-learn Isolation Forest API](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [psutil process CPU and connection APIs](https://psutil.readthedocs.io/stable/)
- [Zeek connection log fields](https://docs.zeek.org/en/current/reference/logs/conn.html)
