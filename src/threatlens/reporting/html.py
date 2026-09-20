from html import escape
from typing import Any


def generate_html_report(
    incidents: list[dict[str, Any]],
) -> str:
    """
    Generate a standalone HTML security report.
    """

    suspicious_count = sum(
        1
        for incident in incidents
        if incident.get("is_suspicious")
    )

    rows = []

    for incident in incidents:
        status = (
            "SUSPICIOUS"
            if incident.get("is_suspicious")
            else "OBSERVATION"
        )

        signals = [
            name
            for name, triggered in incident.get(
                "signals",
                {},
            ).items()
            if bool(triggered)
        ]

        rows.append(
            f"""
            <tr>
                <td>{escape(str(incident["id"]))}</td>
                <td>{escape(str(incident["timestamp"]))}</td>
                <td>{incident["risk_score"]:.0f}</td>
                <td>{escape(str(incident["severity"]))}</td>
                <td>{escape(status)}</td>
                <td>{escape(", ".join(signals) or "None")}</td>
            </tr>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <title>ThreatLens Security Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f5f7fa;
            color: #1f2937;
        }}

        h1 {{
            margin-bottom: 8px;
        }}

        .summary {{
            display: flex;
            gap: 20px;
            margin: 24px 0;
        }}

        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            min-width: 180px;
            box-shadow: 0 2px 8px
                rgba(0, 0, 0, 0.08);
        }}

        .value {{
            font-size: 28px;
            font-weight: bold;
            margin-top: 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}

        th,
        td {{
            padding: 12px;
            border: 1px solid #e5e7eb;
            text-align: left;
        }}

        th {{
            background: #111827;
            color: white;
        }}

        tr:nth-child(even) {{
            background: #f9fafb;
        }}
    </style>
</head>

<body>

    <h1>ThreatLens Security Report</h1>
    <p>
        Behavioral threat detection incident summary.
    </p>

    <div class="summary">

        <div class="card">
            <div>Total Incidents</div>
            <div class="value">
                {len(incidents)}
            </div>
        </div>

        <div class="card">
            <div>Suspicious Incidents</div>
            <div class="value">
                {suspicious_count}
            </div>
        </div>

    </div>

    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Risk</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Signals</th>
            </tr>
        </thead>

        <tbody>
            {"".join(rows)}
        </tbody>
    </table>

</body>
</html>
"""