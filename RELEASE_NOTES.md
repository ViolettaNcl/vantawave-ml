# VantaWave ML v1.0.2

## Authorized Capture Audit patch

- Added Capture Audit page to SOC Dashboard.
- Added authorized-target-bound PCAP/PCAPNG/CAP upload.
- Added target/BSSID/SSID/EAPOL evidence analysis.
- Added optional Aircrack-ng integration.
- Added configurable `VANTAWAVE_AIRCRACK_PATH`.
- Added exactly-one-candidate WPA2 verification.
- Added explicit prevention of multiline wordlist requests.
- Added short-lived in-memory verified-secret vault.
- Added masked verified-secret display.
- Added `Connect verified` without exposing the secret.
- Added optional localhost-only `Copy verified secret`.
- Added tests and documentation.

### Important limitation

This release does not implement `SSID → unknown WPA2/WPA3 password`.
Aircrack-ng-style verification requires authentication evidence and candidate
testing. The dashboard states this explicitly.

---

# VantaWave ML v1.0.1

## Wi-Fi Recovery patch

- Added Wi-Fi Recovery page to the SOC dashboard.
- Added Windows saved-profile inventory.
- Added explicit localhost-only saved-key export.
- Added nearby-network/current-interface/gateway inspection.
- Added local password-strength auditing.
- Added WPA2/WPA3 Windows connection workflow using a supplied passphrase.
- Added saved-profile removal for restoring a clean local state.
- Added CLI recovery commands.
- Added credential-handling safeguards and documentation.

### Important limitation

A laptop that has never connected to an SSID has no saved Windows key for that
SSID. This release does not derive unknown WPA2/WPA3 passwords.

---

# VantaWave ML v1.0.0

## Highlights

- End-to-end Wi-Fi security ML architecture.
- Classical supervised baselines.
- Isolation Forest and PyTorch Autoencoder.
- AWID3-oriented research preprocessing.
- Data-quality and leakage checks.
- Validation/test discipline and threshold calibration.
- Error analysis and model promotion.
- MLflow registry + SHAP support.
- Passive Windows WLAN sensor.
- Offline 802.11 PCAP replay.
- Authorized lab target/session/evidence workflow.
- SQLAlchemy + Alembic + SQLite/PostgreSQL.
- Feature/anomaly-score drift monitoring.
- Retraining recommendations.
- Grounded RAG Security Analyst.
- Restricted read-only agent policy.
- Docker/Compose production stack.
- Professional built-in SOC dashboard.
- Final release and interview-defense documentation.

## Validation

The repository passes its automated test and release-validation suite.

Real external-dataset and authorized live-hardware validation remain separate
evidence-generating steps and are not fabricated in this release.
