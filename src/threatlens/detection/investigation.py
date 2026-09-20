from typing import Any


class IncidentInvestigator:
    """Analyze stored incident evidence."""

    def investigate(
        self,
        incident: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate an investigation summary for an incident."""

        risk_score = float(incident["risk_score"])
        severity = str(incident["severity"])

        signals = incident.get("signals", {})

        triggered_signals = [
            name
            for name, triggered in signals.items()
            if bool(triggered)
        ]

        signal_count = len(triggered_signals)

        if signal_count == 0:
            status = "NO_ANOMALOUS_SIGNALS"
            recommendation = "Continue monitoring."
        elif signal_count == 1:
            status = "SINGLE_SIGNAL"
            recommendation = (
                "Collect additional telemetry before escalating."
            )
        else:
            status = "MULTI_SIGNAL"
            recommendation = (
                "Investigate correlated behavioral anomalies."
            )

        if risk_score >= 80:
            priority = "CRITICAL"
        elif risk_score >= 60:
            priority = "HIGH"
        elif risk_score >= 30:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return {
            "incident_id": incident["id"],
            "status": status,
            "priority": priority,
            "risk_score": risk_score,
            "severity": severity,
            "signal_count": signal_count,
            "triggered_signals": triggered_signals,
            "recommendation": recommendation,
        }
