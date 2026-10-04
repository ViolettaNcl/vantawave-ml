from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import random
import uuid

from vantawave.risk.engine import RiskInput, calculate_risk
from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.features.window import aggregate_events
from vantawave.simulation.scenarios import ScenarioSpec, get_scenario


BASE_BSSID = "02:11:22:33:44:55"
ROGUE_BSSID = "02:11:22:aa:bb:cc"
BASE_SSID = "VantaWave-Lab"
CLIENTS = [
    "02:aa:bb:cc:dd:01",
    "02:aa:bb:cc:dd:02",
    "02:aa:bb:cc:dd:03",
    "02:aa:bb:cc:dd:04",
]


@dataclass(frozen=True)
class FeatureDelta:
    feature: str
    before: float
    after: float
    absolute_change: float

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SimulationResult:
    simulation_id: str
    scenario: dict
    intensity: int
    duration_seconds: int
    baseline_event_count: int
    scenario_event_count: int
    baseline_features: dict
    scenario_features: dict
    feature_deltas: list[dict]
    anomaly_score: float
    classifier_confidence: float
    repeated_alerts: int
    risk: dict
    detections: list[str]
    timeline: list[dict]
    simulated_only: bool
    transmits_packets: bool

    def to_dict(self):
        return asdict(self)


def _event(
    *,
    event_type: EventType,
    at: datetime,
    source: str,
    ssid: str | None = BASE_SSID,
    bssid: str | None = BASE_BSSID,
    transmitter: str | None = BASE_BSSID,
    receiver: str | None = None,
    channel: int | None = 6,
    rssi_dbm: float | None = -48.0,
    retry: bool | None = False,
    security: str | None = "WPA2-Personal",
    metadata: dict | None = None,
) -> WirelessEvent:
    return WirelessEvent(
        event_type=event_type,
        timestamp=at.isoformat(),
        source=source,
        ssid=ssid,
        bssid=bssid,
        transmitter=transmitter,
        receiver=receiver,
        channel=channel,
        rssi_dbm=rssi_dbm,
        retry=retry,
        security=security,
        metadata=dict(metadata or {}),
    )


def generate_baseline(
    *,
    duration_seconds: int = 60,
    seed: int = 42,
) -> list[WirelessEvent]:
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events: list[WirelessEvent] = []

    # Quiet beacon traffic.
    for second in range(0, duration_seconds, 3):
        events.append(
            _event(
                event_type=EventType.BEACON,
                at=start + timedelta(seconds=second),
                source="simulation-baseline",
                receiver="ff:ff:ff:ff:ff:ff",
                rssi_dbm=-48.0 + rng.uniform(-2.5, 2.5),
            )
        )

    # A few normal associations/authentications.
    for index, second in enumerate((8, 26, 44)):
        client = CLIENTS[index % len(CLIENTS)]
        events.extend(
            [
                _event(
                    event_type=EventType.AUTHENTICATION,
                    at=start + timedelta(seconds=second),
                    source="simulation-baseline",
                    transmitter=client,
                    receiver=BASE_BSSID,
                    rssi_dbm=-55 + rng.uniform(-2, 2),
                    metadata={"simulated_result": "accepted"},
                ),
                _event(
                    event_type=EventType.ASSOCIATION,
                    at=start + timedelta(seconds=second + 1),
                    source="simulation-baseline",
                    transmitter=client,
                    receiver=BASE_BSSID,
                    rssi_dbm=-54 + rng.uniform(-2, 2),
                ),
            ]
        )

    # Normal data with low retry rate.
    for second in range(5, duration_seconds, 2):
        client = CLIENTS[(second // 2) % len(CLIENTS)]
        events.append(
            _event(
                event_type=EventType.DATA,
                at=start + timedelta(seconds=second),
                source="simulation-baseline",
                transmitter=client,
                receiver=BASE_BSSID,
                rssi_dbm=-53 + rng.uniform(-3, 3),
                retry=rng.random() < 0.05,
            )
        )

    return sorted(events, key=lambda item: item.timestamp)


def _scenario_events(
    spec: ScenarioSpec,
    *,
    intensity: int,
    duration_seconds: int,
    seed: int,
) -> tuple[list[WirelessEvent], list[dict]]:
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events: list[WirelessEvent] = []
    timeline: list[dict] = []

    factor = max(1, min(5, int(intensity)))

    if spec.scenario_id == "deauth_burst":
        count = 8 * factor
        for i in range(count):
            second = 20 + (i % max(1, min(20, duration_seconds - 20)))
            client = CLIENTS[i % len(CLIENTS)]
            events.append(
                _event(
                    event_type=EventType.DEAUTHENTICATION,
                    at=start + timedelta(seconds=second, milliseconds=i * 7),
                    source="simulation-deauth",
                    transmitter=BASE_BSSID,
                    receiver=client,
                    rssi_dbm=-49 + rng.uniform(-2, 2),
                    metadata={"simulation": True, "reason": "management-frame burst"},
                )
            )
        timeline.append(
            {"second": 20, "event": "synthetic_deauth_burst", "count": count}
        )

    elif spec.scenario_id == "rogue_ap_presence":
        count = 8 + 3 * factor
        for i in range(count):
            second = 18 + (i % max(1, duration_seconds - 18))
            events.append(
                _event(
                    event_type=EventType.BEACON,
                    at=start + timedelta(seconds=second),
                    source="simulation-rogue-ap",
                    ssid=BASE_SSID,
                    bssid=ROGUE_BSSID,
                    transmitter=ROGUE_BSSID,
                    receiver="ff:ff:ff:ff:ff:ff",
                    channel=11,
                    rssi_dbm=-61 + rng.uniform(-2, 2),
                    security="Open" if factor >= 3 else "WPA2-Personal",
                    metadata={
                        "simulation": True,
                        "identity_conflict": True,
                        "expected_authorized_bssid": BASE_BSSID,
                    },
                )
            )
        timeline.append(
            {
                "second": 18,
                "event": "synthetic_duplicate_ssid_bssid",
                "bssid": ROGUE_BSSID,
            }
        )

    elif spec.scenario_id == "auth_storm":
        count = 12 * factor
        for i in range(count):
            second = 12 + (i % max(1, duration_seconds - 12))
            client = f"02:de:ad:00:{i // 256:02x}:{i % 256:02x}"
            events.append(
                _event(
                    event_type=EventType.AUTHENTICATION,
                    at=start + timedelta(seconds=second, milliseconds=i * 5),
                    source="simulation-auth-storm",
                    transmitter=client,
                    receiver=BASE_BSSID,
                    rssi_dbm=-58 + rng.uniform(-5, 5),
                    metadata={"simulation": True, "simulated_result": "rejected"},
                )
            )
        timeline.append(
            {"second": 12, "event": "synthetic_authentication_storm", "count": count}
        )

    elif spec.scenario_id == "retry_storm":
        count = 18 * factor
        for i in range(count):
            second = 10 + (i % max(1, duration_seconds - 10))
            client = CLIENTS[i % len(CLIENTS)]
            events.append(
                _event(
                    event_type=EventType.DATA,
                    at=start + timedelta(seconds=second, milliseconds=i * 4),
                    source="simulation-retry-storm",
                    transmitter=client,
                    receiver=BASE_BSSID,
                    rssi_dbm=-60 + rng.uniform(-10, 8),
                    retry=True,
                    metadata={"simulation": True, "radio_quality": "degraded"},
                )
            )
        timeline.append(
            {"second": 10, "event": "synthetic_retry_storm", "count": count}
        )

    elif spec.scenario_id == "credential_pressure":
        count = 10 * factor
        for i in range(count):
            second = 15 + (i % max(1, duration_seconds - 15))
            client = CLIENTS[i % len(CLIENTS)]
            events.append(
                _event(
                    event_type=EventType.AUTHENTICATION,
                    at=start + timedelta(seconds=second, milliseconds=i * 6),
                    source="simulation-credential-pressure",
                    transmitter=client,
                    receiver=BASE_BSSID,
                    rssi_dbm=-56 + rng.uniform(-3, 3),
                    metadata={
                        "simulation": True,
                        "simulated_result": "rejected",
                        "credential_candidate_tested": False,
                    },
                )
            )
        timeline.append(
            {
                "second": 15,
                "event": "synthetic_rejected_auth_pressure",
                "count": count,
                "password_testing": False,
            }
        )

    return events, timeline


def _numeric_deltas(before: dict, after: dict) -> list[dict]:
    preferred = (
        "event_rate",
        "auth_rate",
        "assoc_rate",
        "deauth_rate",
        "disassoc_rate",
        "beacon_rate",
        "data_rate",
        "unique_bssids",
        "unique_transmitters",
        "rssi_std",
        "retry_ratio",
        "channel_count",
    )
    deltas = []
    for key in preferred:
        if key not in before or key not in after:
            continue
        a = before[key]
        b = after[key]
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            continue
        deltas.append(
            FeatureDelta(
                feature=key,
                before=float(a),
                after=float(b),
                absolute_change=float(b) - float(a),
            ).to_dict()
        )
    return deltas


def _detector_score(
    scenario_id: str,
    baseline: dict,
    current: dict,
    intensity: int,
) -> tuple[float, float, int, list[str], bool]:
    detections: list[str] = []
    factor = max(1, min(5, intensity))

    deauth_delta = current["deauth_rate"] - baseline["deauth_rate"]
    auth_delta = current["auth_rate"] - baseline["auth_rate"]
    retry_delta = current["retry_ratio"] - baseline["retry_ratio"]
    bssid_delta = current["unique_bssids"] - baseline["unique_bssids"]

    anomaly = 0.12
    confidence = 0.50
    repeated = factor
    unknown_device = False

    if deauth_delta > 0.05:
        anomaly += min(0.65, deauth_delta * 2.8)
        confidence = max(confidence, 0.90)
        detections.append("management-frame deauthentication spike")

    if auth_delta > 0.12:
        anomaly += min(0.55, auth_delta * 1.6)
        confidence = max(confidence, 0.86)
        detections.append("authentication-rate spike")

    if retry_delta > 0.35:
        anomaly += min(0.45, retry_delta * 0.7)
        confidence = max(confidence, 0.77)
        detections.append("retry-ratio anomaly")

    if bssid_delta > 0:
        anomaly += 0.48
        confidence = max(confidence, 0.93)
        unknown_device = True
        detections.append("unexpected BSSID for known SSID")

    if scenario_id == "credential_pressure":
        detections.append("repeated rejected-authentication pattern")
        repeated = min(10, 2 * factor)

    anomaly = max(0.0, min(1.0, anomaly))
    confidence = max(0.0, min(1.0, confidence))

    return anomaly, confidence, repeated, detections, unknown_device


def run_simulation(
    scenario_id: str,
    *,
    intensity: int = 3,
    duration_seconds: int = 60,
    seed: int = 42,
) -> SimulationResult:
    spec = get_scenario(scenario_id)

    if not 1 <= int(intensity) <= 5:
        raise ValueError("intensity must be between 1 and 5.")
    if not 30 <= int(duration_seconds) <= 300:
        raise ValueError("duration_seconds must be between 30 and 300.")

    baseline_events = generate_baseline(
        duration_seconds=duration_seconds,
        seed=seed,
    )
    injected_events, timeline = _scenario_events(
        spec,
        intensity=intensity,
        duration_seconds=duration_seconds,
        seed=seed + 100,
    )
    scenario_events = sorted(
        baseline_events + injected_events,
        key=lambda item: item.timestamp,
    )

    baseline_features = aggregate_events(
        baseline_events,
        duration_seconds=duration_seconds,
    ).to_dict()
    scenario_features = aggregate_events(
        scenario_events,
        duration_seconds=duration_seconds,
    ).to_dict()

    anomaly, confidence, repeated, detections, unknown_device = _detector_score(
        scenario_id,
        baseline_features,
        scenario_features,
        intensity,
    )

    risk = calculate_risk(
        RiskInput(
            anomaly_score=anomaly,
            classifier_confidence=confidence,
            repeated_alerts=repeated,
            unknown_device=unknown_device,
        )
    )

    return SimulationResult(
        simulation_id=uuid.uuid4().hex[:12],
        scenario=spec.to_dict(),
        intensity=intensity,
        duration_seconds=duration_seconds,
        baseline_event_count=len(baseline_events),
        scenario_event_count=len(scenario_events),
        baseline_features=baseline_features,
        scenario_features=scenario_features,
        feature_deltas=_numeric_deltas(baseline_features, scenario_features),
        anomaly_score=anomaly,
        classifier_confidence=confidence,
        repeated_alerts=repeated,
        risk={
            "score": risk.score,
            "severity": risk.severity,
            "components": risk.components,
        },
        detections=detections,
        timeline=timeline,
        simulated_only=True,
        transmits_packets=False,
    )
