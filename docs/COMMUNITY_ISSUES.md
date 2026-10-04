# Community Issue Backlog

Create these as real GitHub Issues after the launch-ready commit is green.

## 1. [good first issue] Add Linux passive sensor capability report

**Labels:** `good first issue`, `enhancement`, `sensor`

Add a Linux capability-report adapter that detects available wireless interfaces and documents what passive collection modes are supported. Do not add packet injection or active attacks.

Acceptance criteria:
- Linux capability schema matches the existing sensor capability style.
- No privileged action is executed automatically.
- Unit tests cover available/unavailable states.
- Documentation is updated.

## 2. [research] Reproduce a full external Wi-Fi benchmark

**Labels:** `research`, `machine-learning`, `help wanted`

Run the documented research pipeline on a real external wireless-security dataset under its usage terms.

Acceptance criteria:
- dataset provenance documented;
- fixed train/validation/test split;
- no target leakage;
- F1, precision, recall, PR-AUC, ROC-AUC, FPR/FNR;
- threshold calibration on validation only;
- error analysis;
- reproducible command and report.

## 3. [help wanted] Add dashboard monitoring charts

**Labels:** `help wanted`, `frontend`, `visualization`

Add lightweight charts for feature drift, anomaly-score drift, and evaluation history to the SOC dashboard without duplicating backend business logic.

## 4. [research] Compare Autoencoder vs Isolation Forest under domain shift

**Labels:** `research`, `deep-learning`, `anomaly-detection`

Design a reproducible experiment comparing both anomaly detectors when the current telemetry distribution shifts away from the training baseline.

## 5. [docs] Add Linux/macOS installation notes

**Labels:** `documentation`, `good first issue`

Expand installation documentation for Linux/macOS while clearly marking Windows-only Wi-Fi Recovery functionality.

## 6. [enhancement] Export incident evidence bundle as a single archive

**Labels:** `enhancement`, `evidence`

Add a defensive export workflow that packages incident metadata, cited knowledge references, monitoring context, and SHA-256 evidence manifest into a portable archive. Never include plaintext credentials.
