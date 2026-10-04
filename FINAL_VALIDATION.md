# Final Validation Checklist

## Automated — completed by repository

- [x] Python test suite.
- [x] Python compile check.
- [x] Dashboard route/assets.
- [x] RAG indexing.
- [x] Grounded analyst demo.
- [x] SQLite persistence.
- [x] Alembic migration on SQLite.
- [x] Release file/secret hygiene checks.

## Must be run on the user's Windows machine

- [ ] `python scripts/sensor_capabilities.py`
- [ ] `python scripts/scan_wifi.py --once`
- [ ] dashboard live Windows scan
- [ ] fixed MLflow workflow on the user's exact Windows environment
- [ ] optional PCAP replay with an authorized capture

## Must be run when Docker Desktop is available

- [ ] `docker compose config`
- [ ] `docker compose up --build`
- [ ] PostgreSQL migration
- [ ] `/ready` with required database
- [ ] dashboard through production container

## Required before publishing real model-performance claims

- [ ] Obtain external research dataset under its terms.
- [ ] Run the real research pipeline.
- [ ] Preserve train/validation/test separation.
- [ ] Record error analysis.
- [ ] Record threshold calibration.
- [ ] Store model/report artifacts.
- [ ] Repeat on authorized local telemetry.
- [ ] Compare domain shift between research and local telemetry.

Items above are intentionally not marked complete without evidence from the
actual external dataset/user hardware.


## Wi-Fi Recovery validation

Run on the user's Windows laptop:

- [ ] `python scripts/wifi_recovery.py profiles`
- [ ] `python scripts/wifi_recovery.py scan`
- [ ] `python scripts/wifi_recovery.py status --ssid "<OWN_SSID>"`
- [ ] Confirm that a never-used SSID reports no saved Windows key.
- [ ] Test local password-strength audit.
- [ ] Test connection using the known owner-supplied passphrase.
- [ ] Confirm the network connects.
- [ ] Test `delete-profile` if a clean no-saved-profile state is desired again.
- [ ] If testing saved-key display, explicitly enable
      `VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW=true` and confirm it remains
      accessible only from localhost.

Do not mark "unknown password recovery" as validated: v1.0.1 intentionally
does not implement unknown WPA2/WPA3 password derivation.


## Authorized Capture Audit validation

On the user's authorized lab:

- [ ] Install Scapy extra.
- [ ] Install Aircrack-ng or set `VANTAWAVE_AIRCRACK_PATH`.
- [ ] Register the owned/authorized AP in Authorized Lab.
- [ ] Import an authorized `.pcap/.pcapng/.cap`.
- [ ] Confirm target SSID/BSSID matching.
- [ ] Confirm EAPOL evidence is reported accurately.
- [ ] Test one known-wrong candidate: must not verify.
- [ ] Test the known-correct owner password: must verify when the capture is usable.
- [ ] Confirm dashboard displays a mask, not the plaintext.
- [ ] Confirm `Connect verified` uses the in-memory verified value.
- [ ] Confirm secret copy is unavailable unless local secret viewing is explicitly enabled.
- [ ] Delete local audit artifacts after testing if no longer needed.

Do not mark `SSID-only password recovery` complete; that capability does not
exist in v1.0.2 and is not claimed.


## Adversary Simulation validation

- [x] scenario catalog returns synthetic-only scenarios;
- [x] every scenario reports `transmits_packets = false`;
- [x] deauthentication scenario changes deauth telemetry;
- [x] rogue-AP scenario changes BSSID topology;
- [x] authentication storm changes authentication rate;
- [x] retry storm changes retry telemetry;
- [x] credential-pressure scenario does not test passwords;
- [x] deterministic seed produces repeatable feature/risk output;
- [x] API exposes no active-attack action;
- [x] dashboard labels simulation as synthetic;
- [x] JSON/Markdown report persistence works.

Simulation results are demonstration data and must not be described as observed
real-world attacks.


## Launch readiness

- [x] Apache-2.0 license present.
- [x] package metadata includes repository URLs and license.
- [x] Ruff version pinned.
- [x] CI lint policy is explicit.
- [x] social preview asset is 1280×640.
- [x] read-only static Pages demo present.
- [x] benchmark transparency page present.
- [x] community/launch documentation present.
- [ ] GitHub Topics set in repository settings.
- [ ] GitHub Pages enabled for `main` → `/docs`.
- [ ] social preview uploaded in GitHub Settings.
- [ ] GitHub Release `v1.1.1` created.
- [ ] Discussions enabled.
- [ ] first real external benchmark published.

The unchecked items require repository-admin/UI actions or external benchmark evidence.
