# Security reporting

ThreatLens is an educational behavioral detection prototype. Do not rely on it as the sole protection for critical infrastructure.

If you find an exploitable flaw, use GitHub's private vulnerability reporting option if it is enabled for this repository, or establish a private contact channel with the maintainer before sharing reproduction data. Do not post credentials, real telemetry, private network details or an active exploit against someone else's system in a public issue. Ordinary reproducible bugs using synthetic inputs can be reported in Issues.

Supported work is on the current 0.2 source line. There is no response-time or production-support commitment. Dependency audit results are point-in-time checks, not a guarantee that the project is vulnerability-free.

The threat model, data handling, permissions and known blind spots are documented in `docs/threat-model.md`. Run the minimum necessary profile and protect its state directory and exports with appropriate OS access controls.
