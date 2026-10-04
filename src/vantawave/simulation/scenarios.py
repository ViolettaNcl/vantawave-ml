from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


ScenarioId = Literal[
    "deauth_burst",
    "rogue_ap_presence",
    "auth_storm",
    "retry_storm",
    "credential_pressure",
]


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: ScenarioId
    title: str
    category: str
    description: str
    learning_goal: str
    expected_signals: tuple[str, ...]
    safe_boundary: str
    simulated_only: bool = True
    transmits_packets: bool = False

    def to_dict(self):
        data = asdict(self)
        data["expected_signals"] = list(self.expected_signals)
        return data


SCENARIOS: dict[str, ScenarioSpec] = {
    "deauth_burst": ScenarioSpec(
        scenario_id="deauth_burst",
        title="Deauthentication burst",
        category="802.11 management anomaly",
        description=(
            "Generates a synthetic burst of deauthentication events against an "
            "authorized-lab-shaped topology. No frames are transmitted."
        ),
        learning_goal=(
            "Observe how management-frame spikes change rolling features, risk, "
            "and incident severity."
        ),
        expected_signals=(
            "deauth_rate increases",
            "event_rate increases",
            "risk score increases",
        ),
        safe_boundary="Synthetic event generation only; no radio transmission.",
    ),
    "rogue_ap_presence": ScenarioSpec(
        scenario_id="rogue_ap_presence",
        title="Rogue AP presence",
        category="identity/topology anomaly",
        description=(
            "Adds a synthetic second BSSID advertising the same SSID with a "
            "different channel/security fingerprint."
        ),
        learning_goal=(
            "Study duplicate-SSID and BSSID-topology signals without creating "
            "a real rogue access point."
        ),
        expected_signals=(
            "unique_bssids increases",
            "channel_count increases",
            "duplicate SSID appears",
        ),
        safe_boundary="Synthetic topology only; no AP is created.",
    ),
    "auth_storm": ScenarioSpec(
        scenario_id="auth_storm",
        title="Authentication storm",
        category="authentication anomaly",
        description=(
            "Generates a high-rate synthetic authentication sequence from "
            "multiple simulated clients."
        ),
        learning_goal=(
            "See how repeated authentication pressure appears in telemetry and "
            "risk scoring."
        ),
        expected_signals=(
            "auth_rate increases",
            "unique transmitters increases",
            "event_rate increases",
        ),
        safe_boundary="Synthetic authentication events only.",
    ),
    "retry_storm": ScenarioSpec(
        scenario_id="retry_storm",
        title="Retry storm",
        category="radio/data-quality anomaly",
        description=(
            "Generates synthetic data frames with elevated retry flags and "
            "signal variation."
        ),
        learning_goal=(
            "Differentiate noisy/retry-heavy behavior from management-frame "
            "attack-like patterns."
        ),
        expected_signals=(
            "retry_ratio increases",
            "rssi variation increases",
            "data_rate increases",
        ),
        safe_boundary="Synthetic data-frame metadata only.",
    ),
    "credential_pressure": ScenarioSpec(
        scenario_id="credential_pressure",
        title="Credential guessing pressure",
        category="credential-risk simulation",
        description=(
            "Simulates repeated rejected authentication attempts against a lab "
            "SSID. It does not test or derive real passwords."
        ),
        learning_goal=(
            "Model the defensive telemetry footprint of repeated credential "
            "guessing without performing password attacks."
        ),
        expected_signals=(
            "auth_rate increases",
            "rejected-attempt metadata increases",
            "repeated-alert component increases",
        ),
        safe_boundary=(
            "No password candidates are generated, tested, transmitted, or recovered."
        ),
    ),
}


def list_scenarios() -> list[dict]:
    return [SCENARIOS[key].to_dict() for key in sorted(SCENARIOS)]


def get_scenario(scenario_id: str) -> ScenarioSpec:
    try:
        return SCENARIOS[scenario_id]
    except KeyError as exc:
        raise KeyError(f"Unknown simulation scenario: {scenario_id}") from exc
