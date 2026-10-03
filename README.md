# VantaWave ML

**Wi‑Fi Security, Passive Telemetry, Machine Learning, Deep Anomaly Detection, MLOps & AI Research Platform**

VantaWave ML is an independent portfolio/research project that combines
wireless telemetry, data engineering, classical ML, deep anomaly detection,
MLOps, explainability, risk analysis and — in later releases — authorized
lab validation, persistent monitoring, grounded AI analysis and a SOC-style
interface.

## v0.7 — Passive Wi‑Fi Sensor Layer

v0.7 moves VantaWave from dataset-only experiments toward real telemetry.

### New in v0.7

- normalized `WirelessEvent` schema;
- Windows WLAN discovery adapter using the operating system's `netsh` interface;
- English/Russian `netsh` parser;
- SSID/BSSID/channel/security/signal observations;
- host capability detection;
- JSONL event/session storage;
- rolling event windows;
- live feature aggregation;
- network inventory and AP-change detection;
- offline JSONL replay;
- optional offline 802.11 PCAP/PCAPNG replay through Scapy;
- Dot11 event classification for beacon/auth/association/deauth/disassoc/data frames;
- channel/frequency normalization;
- sensor CLI tools;
- sensor API endpoints;
- CI sensor smoke test;
- expanded automated test suite.

## Important distinction

`WindowsNetshSensor` is **OS-level WLAN discovery**, not raw monitor-mode
802.11 capture. The Windows WLAN stack may control how scanning occurs.

v0.7 does **not** implement:

- packet injection;
- deauthentication transmission;
- active wireless attacks;
- raw live monitor-mode frame capture.

Raw frame-level data is supported only through **offline PCAP replay** in this
release. Hardware/driver-specific live 802.11 capture is deferred to the
authorized-lab phase.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,deep]"
python -m pytest
```

## Check sensor capabilities

```powershell
python scripts/sensor_capabilities.py
```

On Windows this reports whether `netsh` WLAN discovery is available.

## Run one Windows WLAN discovery scan

```powershell
python scripts/scan_wifi.py --once
```

Example event fields:

```text
event_type
timestamp
source
ssid
bssid
channel
signal_percent
estimated rssi_dbm
security
radio_type
```

The `rssi_dbm` value derived from Windows signal quality is explicitly marked
as an estimate in event metadata.

## Record a sensor session

```powershell
python scripts/scan_wifi.py --duration 30 --interval 5 --window 60
```

Generated files:

```text
artifacts/sensors/live/
├── events.jsonl
├── features.jsonl
├── inventory.json
├── inventory_changes.jsonl
└── session.json
```

## Replay stored events

```powershell
python scripts/replay_wifi_events.py artifacts/sensors/live/events.jsonl --window 60
```

## Normalized sensor fixture

For a completely reproducible test:

```powershell
python scripts/generate_sensor_fixture.py
python scripts/replay_wifi_events.py data/demo/sensor_events.jsonl
```

## Offline 802.11 PCAP replay

Install Scapy:

```powershell
pip install -e ".[dev,pcap]"
```

Then analyze an **authorized/offline** Wi‑Fi capture:

```powershell
python scripts/inspect_pcap.py "C:\path\to\capture.pcapng"
```

VantaWave extracts normalized events and aggregates them into rolling-style
features. No packets are transmitted.

## Rolling feature layer

Current window features include:

- total event rate;
- authentication rate;
- association rate;
- deauthentication rate;
- disassociation rate;
- beacon rate;
- data rate;
- AP observation rate;
- unique BSSIDs;
- unique transmitters;
- unique SSIDs;
- RSSI mean/std;
- Windows signal-quality mean;
- retry ratio;
- channel count.

A compatibility projection to the earlier 10-feature ML schema exists for
research experiments, but live telemetry should **not** be fed into a model
trained on unrelated synthetic data and presented as a real prediction.

## API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Open:

`http://127.0.0.1:8000/docs`

New v0.7 endpoints:

- `GET /sensors/capabilities`
- `GET /sensors/schema`
- `GET /sensors/windows/scan`

Existing ML/MLOps endpoints remain available.

## Previous layers retained

v0.7 still includes:

- AWID3-oriented research pipeline;
- threshold calibration;
- error analysis;
- local model registry;
- model promotion;
- optional MLflow;
- SHAP;
- PyTorch Autoencoder;
- Isolation Forest;
- known/unknown anomaly evaluation;
- drift-baseline foundation.

## Research integrity

OS-visible Wi‑Fi discovery and offline PCAP replay are not equivalent to
monitor-mode capture. VantaWave records the collection mode explicitly so
later reports can distinguish data provenance.
