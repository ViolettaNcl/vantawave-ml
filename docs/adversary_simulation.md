# Adversary Simulation

## Goal

The simulation layer lets VantaWave demonstrate the entire red-team → blue-team
feedback loop without transmitting packets or attacking real infrastructure.

```text
Scenario
  ↓
Synthetic WirelessEvent stream
  ↓
Feature aggregation
  ↓
Detection heuristics
  ↓
Risk Engine
  ↓
Incident-style report
```

## Safety contract

Every built-in scenario has:

- `simulated_only = true`
- `transmits_packets = false`
- explicit learning goal
- explicit safety boundary

No real credentials are generated, tested, recovered or transmitted.

## Scenarios

### Deauthentication burst

Injects synthetic `DEAUTHENTICATION` events into a normal baseline.

Expected defensive signals:

- `deauth_rate ↑`
- `event_rate ↑`
- risk score ↑

### Rogue AP presence

Adds a synthetic second BSSID advertising the same SSID with a different
channel/security fingerprint.

Expected signals:

- `unique_bssids ↑`
- `channel_count ↑`
- unexpected-BSSID detector

No real access point is created.

### Authentication storm

Adds many synthetic authentication attempts from multiple simulated clients.

Expected signals:

- `auth_rate ↑`
- `unique_transmitters ↑`
- event rate ↑

### Retry storm

Adds retry-heavy synthetic data frames.

Expected signals:

- `retry_ratio ↑`
- RSSI variance ↑
- data rate ↑

This scenario is useful for distinguishing radio-quality anomalies from
management/authentication anomalies.

### Credential pressure

Models repeated rejected authentication events.

It deliberately does **not**:

- generate password candidates;
- test passwords;
- perform brute force;
- transmit authentication attempts.

It exists to demonstrate the **defensive telemetry footprint** of credential
pressure.

## CLI

List scenarios:

```powershell
python scripts/run_adversary_simulation.py --list
```

Run:

```powershell
python scripts/run_adversary_simulation.py auth_storm --intensity 3
```

Parameters:

```text
--intensity 1..5
--duration 30..300
--seed <integer>
--no-save
```

Default reports:

```text
artifacts/simulation/reports/
```

## API

```text
GET  /simulation/capabilities
GET  /simulation/scenarios
POST /simulation/run
```

Example request:

```json
{
  "scenario_id": "rogue_ap_presence",
  "intensity": 3,
  "duration_seconds": 60,
  "seed": 42,
  "persist_report": true
}
```

## Portfolio value

This layer makes it possible to demonstrate:

- security telemetry engineering;
- feature behavior under controlled conditions;
- anomaly reasoning;
- risk scoring;
- scenario reproducibility;
- red-team / blue-team thinking;
- safe security experimentation.
