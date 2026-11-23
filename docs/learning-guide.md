# Learn ThreatLens gradually

## Start with the purpose

An IoC is a previously recognized clue, such as a malicious file hash or address. A behavior detector instead asks whether a device is acting differently from a trusted normal profile. That can help when a threat is unknown, but different behavior can also be a harmless backup. ThreatLens reports evidence to investigate; it cannot know intent from aggregate numbers alone.

The project is a Python CLI. A shell command invokes Python functions through Typer. There is no Electron desktop window, Android package, large language model API or neural-network training service in this repository.

## Follow one observation

Take a network metric `bytes_out`. Suppose a sensor normally reports approximately 10,000 bytes per configured window and now reports 100,000. The parser validates its identity, time and units. The service loads that sensor's trusted history. Robust statistics compare the new number with the baseline median and variation. Isolation Forest evaluates the whole source feature vector. The application combines those results and asks whether another source also changed or whether the same behavior persisted. It then returns a status, priority and explanation and may save an incident.

Read these files in order:

1. `cli/app.py`: command registration, the application's entry point.
2. `cli/commands/scan.py`: loads input or collects data, calls the service, prints results.
3. `schema/device.py`: the exact input contract and validation rules.
4. `detection/device.py`: trusted learning, assessment, persistence and transactions.
5. `models/isolation_forest.py` and `detection/behavioral.py`: the two detector components.
6. `storage/database.py` and `storage/repositories.py`: state and saved evidence.
7. `evaluation/device_benchmark.py`: the experiment, labels and measured limitations.

## A five-session learning path

| Session | Do this | Be able to explain |
| --- | --- | --- |
| 1 | Install; run help and the isolated demo | CLI, observation, baseline and incident |
| 2 | Open one baseline and suspicious JSON file | Identity, source, metric, window and timestamp |
| 3 | Read the robust detector and change a copy of an example | Median, MAD, thresholds and tiny-change protection |
| 4 | Read Isolation Forest and the source-consensus function | Unsupervised training, decision score and persistence |
| 5 | Run tests, benchmark and build | Engineering correctness versus real security effectiveness |

Do experiments in a fresh state directory. The scan command rejects replayed timestamps; reusing the same example against the same state is supposed to fail. Use a fresh demo directory or explicitly relearn with `--replace` when you intend to reset a synthetic experiment.

## Questions you should be ready to answer

**Why is this AI/ML?** Isolation Forest learns a distribution from trusted feature vectors without attack-class labels. Statistical checks and application rules complement that model.

**Is this an LLM?** No. It uses scikit-learn's Isolation Forest and numerical statistics. It does not send prompts or telemetry to a cloud AI service.

**Why not use just CPU?** Many normal workloads consume CPU. Network, process, routing and firewall changes provide context, although they can still be correlated with benign work.

**What is MAD?** The median of absolute distances from the baseline median. It is less affected by extreme historical values than a simple mean and standard deviation. Near-zero MAD needs a meaningful-change floor.

**What does Isolation Forest do?** It uses random partitioning trees to isolate feature vectors. Unusual observations may be isolated more easily. Its decision function is negative for outliers under the learned threshold.

**Why thirty observations?** It is the implementation's minimum to avoid immediate scoring on a handful of samples. It is not a mathematically proven sample-size guarantee. Real baselines need enough representative normal activity.

**How do you avoid learning an attack as normal?** Scans never update the trusted baseline. Only explicit `learn` operations do, so the operator must verify the training period and review relearning.

**Does a 70 risk score mean a 70% chance of compromise?** No. It is a heuristic investigation priority computed from source evidence and persistence.

**Why not claim 100% accuracy?** The original toy benchmark tested a small statistical component. The current benchmark includes cases that expose false alarms and missed attacks. Even good synthetic results do not establish real-world security performance.

**Can it detect an unknown attack?** It may detect an unknown attack if that attack changes the measured behavior. An attack that preserves those metrics may evade it, as the stealth example demonstrates.

**Does router support mean it logs into my router?** No. An upstream exporter maps device metrics to the versioned JSON contract. There is no built-in vendor login or SNMP collector. Zeek logs provide a separate native network import path.

**Where is the data stored?** In a local SQLite database selected by `THREATLENS_DATA_DIR`; the default is `~/.threatlens/threatlens.db`. Incident evidence and bounded trusted profiles persist across invocations.

**Why keep the last observation separate from training?** A suspicious sample still matters for the next temporal comparison, but it should not change the definition of normal behavior.

**What happens when access is denied?** The source is unavailable or degraded. It is never treated as a normal zero-activity observation. A narrower profile must be selected deliberately during learning and scanning.

**How can someone use this CLI later?** A wheel can be installed with pip in a compatible Python environment. A native executable would require a separate packaging and platform-testing step. No hosting is required for local inference.

## Exercises

- Run a single-source spike and observe `REVIEW`, then a second comparable window and observe escalation.
- Remove a trained source from a copied input and inspect `coverage.degraded`.
- Change a feature name and explain why silently guessing a replacement would be unsafe.
- Compare the full detector's FPR with each ablation, then explain why shared synthetic patterns limit the conclusion.
- Trace one saved incident's explanation back to the exact feature values and score calculation.
