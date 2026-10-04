import pytest

from vantawave.simulation.engine import run_simulation
from vantawave.simulation.scenarios import get_scenario, list_scenarios


def test_scenarios_are_explicitly_synthetic():
    scenarios = list_scenarios()
    assert len(scenarios) >= 5
    assert all(item["simulated_only"] is True for item in scenarios)
    assert all(item["transmits_packets"] is False for item in scenarios)


def test_deauth_burst_changes_deauth_rate_and_risk():
    result = run_simulation(
        "deauth_burst",
        intensity=4,
        duration_seconds=60,
        seed=42,
    )
    assert result.transmits_packets is False
    assert result.simulated_only is True
    assert result.scenario_features["deauth_rate"] > result.baseline_features["deauth_rate"]
    assert result.risk["score"] > 0
    assert any("deauthentication" in item for item in result.detections)


def test_rogue_ap_adds_bssid():
    result = run_simulation(
        "rogue_ap_presence",
        intensity=3,
        duration_seconds=60,
        seed=42,
    )
    assert result.scenario_features["unique_bssids"] > result.baseline_features["unique_bssids"]
    assert any("BSSID" in item for item in result.detections)


def test_credential_pressure_does_not_test_real_passwords():
    result = run_simulation(
        "credential_pressure",
        intensity=5,
        duration_seconds=60,
        seed=42,
    )
    assert result.transmits_packets is False
    assert "password" in result.scenario["safe_boundary"].lower()
    assert result.repeated_alerts >= 1


def test_simulation_is_deterministic_for_same_seed():
    first = run_simulation("retry_storm", intensity=3, seed=7)
    second = run_simulation("retry_storm", intensity=3, seed=7)
    assert first.scenario_features == second.scenario_features
    assert first.risk == second.risk


def test_invalid_intensity_rejected():
    with pytest.raises(ValueError):
        run_simulation("deauth_burst", intensity=6)


def test_unknown_scenario_rejected():
    with pytest.raises(KeyError):
        get_scenario("not-a-scenario")
