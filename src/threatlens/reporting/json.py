import json
from typing import Any


def generate_json_report(
    incidents: list[dict[str, Any]],
) -> str:
    """
    Generate a machine-readable JSON report.
    """

    suspicious_count = sum(
        1
        for incident in incidents
        if incident.get("is_suspicious")
    )

    payload = {
        "summary": {
            "total_incidents": len(incidents),
            "suspicious_incidents": suspicious_count,
        },
        "incidents": incidents,
    }

    return json.dumps(
        payload,
        indent=2,
    )