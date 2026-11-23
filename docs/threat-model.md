# Threat model and privacy

ThreatLens is a read-only behavioral investigation aid. Its monitored assets are aggregate resource usage, process metadata and socket behavior, imported routing/firewall metrics, trusted training data, incident evidence, and reports. It runs without a mandatory cloud connection and performs inference locally.

## Trust boundaries

| Boundary | Assumption and control | Residual limit |
| --- | --- | --- |
| OS to collectors | psutil APIs; visible permission failures and incomplete source status | A privileged attacker can alter or conceal telemetry; Linux may silently omit some restricted connections |
| Import to parser | 10 MiB input bound, schema vocabulary, finite numbers, identity and timestamp validation | Syntactically valid forged telemetry is still possible |
| Operator to baseline | Explicit trusted learning; scans never retrain; profiles are device-specific | Initial compromise or careless relearning can poison the baseline |
| CLI to SQLite | Parameterized queries, writer transactions, additive migration, owner-only new files | No encryption, digital signatures, tamper-evident history or remote replication |
| Database to report | Escaped HTML, no external scripts, restrictive CSP, exclusive private file creation | Authorized readers can disclose the report; file protection depends on OS and account controls |
| Sensor identity to profile | Device type and stable ID choose a baseline | Identity is not cryptographically authenticated |

The parser rejects unknown feature names and mismatched windows rather than substituting fabricated values. Missing trained sources are reported as degraded. An error, a quiet scan or an absent alert is never evidence that a device is clean.

## Expected failure modes

Benign builds, backups and scheduled jobs may look suspicious. The source-consensus and persistence policy reduces transient alerts but cannot infer user intent. Conversely, malware that stays within normal aggregate behavior, runs between observations, or tampers with collectors may evade detection. Multiple source domains may reflect the same legitimate event.

The software does not block connections, kill processes, modify firewall rules, exploit services, capture packets, or perform remediation. A report should lead to contextual investigation and corroboration with independent records. It is not a forensic conclusion.

## Sensitive data

Raw local collection temporarily reads process names, usernames and network endpoints. The current device service stores aggregate features and their explanations, not the raw process table or endpoint identities. Zeek conversion validates endpoint syntax and retains counts and bytes, not the endpoint strings. Existing 0.1 incident data and operator-supplied files may have different content; inspect before sharing.

New database and exported files use POSIX mode 0600; new state directories use 0700. Existing paths retain their existing permissions. Windows access control follows the user directory and OS ACLs rather than these POSIX bits. Reports are not encrypted. Protect or remove the selected state directory according to your institution's retention rules; back up the SQLite file only when writers are stopped or using SQLite's backup API.

Do not commit real telemetry, databases, credentials or incident reports. The checked-in examples are generated synthetic metrics. `THREATLENS_DATA_DIR` is configuration, not a secret, and `.env` is not loaded automatically. The preserved all-rights-reserved license controls reuse separately from technical installability.
