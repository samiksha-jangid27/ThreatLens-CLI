"""The deployed detector: per-device training, source consensus, frozen baselines."""

import json
from typing import Any

from threatlens.detection.behavioral import BehavioralDeviationDetector
from threatlens.detection.risk import RiskScorer
from threatlens.models.isolation_forest import IsolationForestDetector
from threatlens.schema.device import DeviceObservation, timestamp_value
from threatlens.storage.repositories import IncidentRepository

MIN_BASELINE = 30
MAX_BASELINE = 500
ALGORITHM_VERSION = "source-consensus-v1"


def assess_observation(current: DeviceObservation, baseline: list[dict], previous: dict | None = None,
                       streaks: dict[str, int] | None = None) -> dict[str, Any]:
    """Pure assessment used by both the CLI and the full-pipeline benchmark."""
    first = baseline[0]
    if current.window_seconds != first["window_seconds"]:
        raise ValueError("Observation window differs from baseline; use the same window_seconds")
    known = first["sources"]
    if set(current.sources) - set(known):
        raise ValueError("New source requires explicit baseline replacement")
    missing = sorted(set(known) - set(current.sources))
    details, confirmed, reviews, next_streaks = {}, [], [], {}
    evidence = []
    comparable_previous = previous is not None and (
        current.window_seconds * 0.5 <=
        (timestamp_value(current.timestamp) - timestamp_value(previous["timestamp"])).total_seconds()
        <= max(300, 5 * current.window_seconds)
    )
    for source, features in current.sources.items():
        if set(features) != set(known[source]):
            raise ValueError(f"{source} feature names differ from baseline; explicitly relearn this profile")
        rows = [row["sources"][source] for row in baseline]
        model = IsolationForestDetector(contamination=0.05)
        model.fit(rows)
        ml = model.predict(features)
        robust = BehavioralDeviationDetector(threshold=3.5).analyze(features, rows)
        extreme = any(abs(value["z_score"]) >= 6 for value in robust["signals"].values())
        corroborated = robust["is_anomaly"] and (ml["is_anomaly"] or extreme)
        if corroborated:
            confirmed.append(source)
        if robust["is_anomaly"] or ml["is_anomaly"]:
            reviews.append(source)
        prior_count = (streaks or {}).get(source, 0) if comparable_previous else 0
        next_streaks[source] = prior_count + 1 if corroborated else 0
        old_features = (previous or {}).get("sources", {}).get(source, {})
        for name in robust["anomalous_features"]:
            value = robust["signals"][name]
            evidence.append({
                "signal": source, "description": f"{source}.{name} deviates from its trusted baseline.",
                "details": {"feature": name, "current": features[name],
                            "baseline_median": value["baseline_median"], "mad": value["mad"],
                            "robust_z_score": value["z_score"],
                            "delta": features[name] - old_features[name] if name in old_features else None},
            })
        if ml["is_anomaly"]:
            evidence.append({"signal": source, "description": f"Isolation Forest flagged the {source} feature vector.",
                             "details": {"anomaly_score": ml["anomaly_score"], "score_direction": "negative is anomalous"}})
        details[source] = {"model": ml, "behavioral": robust, "corroborated": bool(corroborated),
                           "consecutive_anomalies": next_streaks[source]}
    persistent = [name for name in confirmed if next_streaks[name] >= 2]
    suspicious = len(confirmed) >= 2 or bool(persistent)
    contributions = {name: 25.0 for name in confirmed}
    if any(details[name]["model"]["is_anomaly"] for name in confirmed):
        contributions["model_corroboration"] = 10.0
    if persistent:
        contributions["persistence"] = 20.0
    score = min(100.0, sum(contributions.values()))
    if reviews and not contributions:
        score = 10.0
    severity = RiskScorer._severity(score)
    status = "SUSPICIOUS" if suspicious else "REVIEW" if reviews else "NO_CORRELATED_ANOMALY"
    return {
        "algorithm_version": ALGORITHM_VERSION, "device_id": current.device_id, "device_type": current.device_type,
        "timestamp": current.timestamp, "status": status, "is_suspicious": suspicious,
        "coverage": {"assessed_sources": sorted(details), "missing_sources": missing,
                     "unavailable": current.unavailable, "degraded": bool(missing or current.unavailable)},
        "signals": {name: name in confirmed for name in current.sources},
        "correlation": {"is_correlated": suspicious, "triggered_signals": confirmed,
                        "signal_count": len(confirmed), "persistent_sources": persistent},
        "risk": {"risk_score": score, "severity": severity, "contributions": contributions,
                 "triggered_signals": confirmed, "meaning": "heuristic investigation priority, not probability"},
        "explanation": {"risk_score": score, "severity": severity, "evidence": evidence, "evidence_count": len(evidence),
                        "summary": f"{len(confirmed)} source(s) corroborated; {len(persistent)} persistent. An anomaly does not prove compromise."},
        "features": current.sources, "sources": details, "streaks": next_streaks, "baseline_size": len(baseline),
    }


class DeviceDetectionService:
    def __init__(self, repository: IncidentRepository):
        self.repository = repository
        self.database = repository.database

    @staticmethod
    def _key(observation: DeviceObservation) -> str:
        return f"{observation.device_type}:{observation.device_id}"

    @staticmethod
    def _save(connection, key: str, state: dict) -> None:
        connection.execute("INSERT INTO device_state VALUES (?, ?) ON CONFLICT(device_key) DO UPDATE SET state=excluded.state",
                           (key, json.dumps(state, allow_nan=False)))

    def learn(self, observations: list[DeviceObservation], replace: bool = False) -> dict:
        if not observations:
            raise ValueError("No trusted observations provided")
        key = self._key(observations[0])
        with self.database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT state FROM device_state WHERE device_key=?", (key,)).fetchone()
            state = json.loads(row["state"]) if row is not None and not replace else {"baseline": []}
            baseline = state["baseline"]
            for observation in observations:
                if self._key(observation) != key or observation.unavailable:
                    raise ValueError("Learning requires one device and complete, trusted telemetry")
                data = observation.to_dict()
                if baseline:
                    first = baseline[0]
                    if data["window_seconds"] != first["window_seconds"] or {k: set(v) for k, v in data["sources"].items()} != {k: set(v) for k, v in first["sources"].items()}:
                        raise ValueError("Learning feature schema or window mismatch; use --replace deliberately")
                    last_time = state.get("previous", baseline[-1])["timestamp"]
                    if timestamp_value(data["timestamp"]) <= timestamp_value(last_time):
                        raise ValueError("Learning timestamps must be newer than stored observations")
                baseline.append(data)
                state["previous"] = data
            state["baseline"] = baseline[-MAX_BASELINE:]
            state["streaks"] = {}
            self._save(connection, key, state)
            return {"device": key, "baseline_size": len(state["baseline"]), "required": MIN_BASELINE,
                    "ready": len(state["baseline"]) >= MIN_BASELINE, "baseline_policy": "frozen; explicit learning only"}

    def scan(self, observations: list[DeviceObservation]) -> list[dict]:
        results = []
        # A malformed/replayed later window rolls back the entire input batch.
        with self.database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for observation in observations:
                key = self._key(observation)
                row = connection.execute("SELECT state FROM device_state WHERE device_key=?", (key,)).fetchone()
                state = json.loads(row["state"]) if row is not None else {"baseline": []}
                baseline = state["baseline"]
                if len(baseline) < MIN_BASELINE:
                    results.append({"device_id": observation.device_id, "device_type": observation.device_type,
                                    "status": "INSUFFICIENT_BASELINE", "is_suspicious": False,
                                    "baseline_size": len(baseline), "required": MIN_BASELINE})
                    continue
                previous = state.get("previous")
                if previous and timestamp_value(observation.timestamp) <= timestamp_value(previous["timestamp"]):
                    raise ValueError("Replayed/out-of-order telemetry; timestamp must be newer than stored observations")
                result = assess_observation(observation, baseline, previous, state.get("streaks"))
                if result["is_suspicious"]:
                    result["incident_id"] = self.repository.create(result, connection)
                # Previous means the last scan, even if suspicious. Never train on it.
                state["previous"] = observation.to_dict()
                state["streaks"] = result["streaks"]
                self._save(connection, key, state)
                results.append(result)
        return results

    def status(self) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM device_state ORDER BY device_key").fetchall()
        return [{"device": row["device_key"], "baseline_size": len(json.loads(row["state"])["baseline"]),
                 "ready": len(json.loads(row["state"])["baseline"]) >= MIN_BASELINE,
                 "last_observation": json.loads(row["state"]).get("previous", {}).get("timestamp")} for row in rows]
