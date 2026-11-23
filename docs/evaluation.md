# Evaluation

The default `threatlens benchmark` now calls the same `assess_observation` function used by the CLI. The original ten-scenario statistical benchmark is retained only as `benchmark --component`. Its perfect toy score does not describe the complete application.

## Reproducible design

Run `threatlens benchmark --json`. The seed is 42. Each of four profiles has 60 synthetic training windows, generated separately from held-out assessment scenarios. No scenario observation is added to training. Temporal state resets between scenarios and advances within a scenario, so tests can measure persistence without contamination from a previous scenario.

Each profile runs eight scenarios: normal activity, benign jitter, transient transfer, recovery after transfer, sustained simulated exfiltration, simulated changes across sources, an authorized backup, and a stealth attack with normal-looking metrics. The last two intentionally expose unresolved false positives and false negatives. A scenario is predicted positive if any of its windows alerts.

Device profiles cover system/network/process, router system/network/routing, firewall network/firewall, and network-only feature maps. They use the same scenario patterns and do not represent independent real-device samples. Labels encode simulated intent; the input itself cannot distinguish an authorized backup from an identical malicious transfer.

## Recorded results

The seed 42 run on 23 November 2026 produced:

| Method | TP | TN | FP | FN | Accuracy | Precision | Recall | F1 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full detector | 8 | 16 | 4 | 4 | 75.00% | 66.67% | 66.67% | 66.67% | 20.00% |
| Isolation Forest only | 8 | 8 | 12 | 4 | 50.00% | 40.00% | 66.67% | 50.00% | 60.00% |
| Robust statistics only | 8 | 8 | 12 | 4 | 50.00% | 40.00% | 66.67% | 50.00% | 60.00% |

Each individual profile has TP 2, TN 4, FP 1 and FN 1. A sustained single-source anomaly alerts on its second comparable window. `alert_window` reports that count; it is not an end-to-end latency measurement on real sensors. The two ablations classify a scenario positive if their method flags any source/window, so their lower FPR comparison illustrates this scenario policy, not a controlled empirical superiority claim.

The aggregate confusion matrix is:

| Ground truth | Predicted suspicious | Predicted not suspicious |
| --- | ---: | ---: |
| Simulated compromise | 8 | 4 |
| Simulated benign | 4 | 16 |

Metrics are computed from boolean label lists of equal length. Zero-denominator cases return zero. FPR is FP/(FP+TN); recall and detection rate are TP/(TP+FN). Overall accuracy alone is insufficient for imbalanced security data.

## Engineering verification

Tests cover parsing, finite numeric validation, collector permissions, feature extraction, baseline isolation, replay and schema rejection, frozen training, previous-window advancement, persistence and gap reset, alert deduplication, atomic rollback, SQLite migration, evidence retention, output permissions, report escaping, CLI integration, and evaluation. Host-related unit tests use deterministic mocks so permissions and workloads do not change results.

CI defines test jobs for Linux, macOS and Windows on Python 3.11 and 3.14, and a separate wheel/source build with installed-entry-point checks. Defined jobs are not evidence that those platforms passed: consult the actual run linked in the validation record. Local verification is recorded separately.

## Limits and next experiment

No real compromised-device dataset, hardware firewall, physical router, or confirmed intrusion was available in this review. The measured rates are synthetic, not production estimates. Thirty training windows can be too few; training should cover known normal workload modes, periods and maintenance activity. Low-frequency observations can miss brief attacks. Blind spots remain for attacker behavior that preserves aggregate metrics, tampered telemetry, and compromised baseline collection.

A subsequent empirical study should reserve held-out devices and later time periods, obtain independently verified labels, include authorized backups and maintenance, specify sampling and attack onset times, and report per-device FPR, precision/recall, detection delay, memory/CPU overhead and confidence intervals. Thresholds should be chosen on validation data and frozen before testing. Public flow datasets may support network experiments after explicit feature mapping, but are not interchangeable with endpoint, routing or firewall ground truth.
