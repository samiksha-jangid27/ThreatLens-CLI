from typing import Any


class ThreatExplainer:
    """
    Convert detection signals into human-readable evidence.
    """

    def explain(
        self,
        detection_result: dict[str, Any],
    ) -> dict[str, Any]:
        evidence: list[dict[str, Any]] = []

        signals = detection_result.get(
            "signals",
            {},
        )

        model = detection_result.get(
            "model",
            {},
        )

        behavioral = detection_result.get(
            "behavioral"
        )

        network = detection_result.get(
            "network"
        )

        process = detection_result.get(
            "process"
        )

        risk = detection_result.get(
            "risk",
            {},
        )

        # -------------------------------------------------
        # ISOLATION FOREST
        # -------------------------------------------------

        if signals.get("isolation_forest"):
            evidence.append(
                {
                    "signal": "isolation_forest",
                    "description": (
                        "Current system behavior was "
                        "classified as anomalous by "
                        "the Isolation Forest model."
                    ),
                    "details": {
                        "anomaly_score": model.get(
                            "anomaly_score"
                        )
                    },
                }
            )

        # -------------------------------------------------
        # TEMPORAL ANOMALY
        # -------------------------------------------------

        if signals.get("temporal_anomaly"):
            temporal = detection_result.get(
                "temporal",
                {},
            )

            evidence.append(
                {
                    "signal": "temporal_anomaly",
                    "description": (
                        "System telemetry changed "
                        "significantly compared with "
                        "the previous observation."
                    ),
                    "details": {
                        "signal_count": temporal.get(
                            "signal_count",
                            0,
                        ),
                        "triggered_signals": temporal.get(
                            "triggered_signals",
                            {},
                        ),
                    },
                }
            )

        # -------------------------------------------------
        # SYSTEM BEHAVIORAL DEVIATION
        # -------------------------------------------------

        if signals.get("behavioral_deviation"):
            anomalous_features = []

            if behavioral:
                anomalous_features = behavioral.get(
                    "anomalous_features",
                    [],
                )

            evidence.append(
                {
                    "signal": "behavioral_deviation",
                    "description": (
                        "Current system behavior "
                        "deviates significantly from "
                        "the learned behavioral baseline."
                    ),
                    "details": {
                        "anomalous_features": (
                            anomalous_features
                        )
                    },
                }
            )

        # -------------------------------------------------
        # NETWORK ANOMALY
        # -------------------------------------------------

        if signals.get("network_anomaly"):
            network_behavioral = None

            if network:
                network_behavioral = network.get(
                    "behavioral"
                )

            anomalous_features = []

            if network_behavioral:
                anomalous_features = (
                    network_behavioral.get(
                        "anomalous_features",
                        [],
                    )
                )

            evidence.append(
                {
                    "signal": "network_anomaly",
                    "description": (
                        "Network behavior deviates "
                        "from the learned network baseline."
                    ),
                    "details": {
                        "anomalous_features": (
                            anomalous_features
                        )
                    },
                }
            )

        # -------------------------------------------------
        # PROCESS ANOMALY
        # -------------------------------------------------

        if signals.get("process_anomaly"):
            process_behavioral = None

            if process:
                process_behavioral = process.get(
                    "behavioral"
                )

            anomalous_features = []

            if process_behavioral:
                anomalous_features = (
                    process_behavioral.get(
                        "anomalous_features",
                        [],
                    )
                )

            evidence.append(
                {
                    "signal": "process_anomaly",
                    "description": (
                        "Process behavior deviates "
                        "from the learned process baseline."
                    ),
                    "details": {
                        "anomalous_features": (
                            anomalous_features
                        )
                    },
                }
            )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        risk_score = float(
            risk.get(
                "risk_score",
                0.0,
            )
        )

        severity = str(
            risk.get(
                "severity",
                "LOW",
            )
        )

        return {
            "risk_score": risk_score,
            "severity": severity,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "summary": self._build_summary(
                evidence,
                risk_score,
                severity,
            ),
        }

    @staticmethod
    def _build_summary(
        evidence: list[dict[str, Any]],
        risk_score: float,
        severity: str,
    ) -> str:
        if not evidence:
            return (
                "No anomalous behavioral evidence "
                "was identified."
            )

        return (
            f"{len(evidence)} behavioral signal(s) "
            f"contributed to a {severity} risk assessment "
            f"with a score of {risk_score:.0f}/100."
        )