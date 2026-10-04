<div align="center">

<img src="docs/assets/vantawave-hero.gif" alt="VantaWave ML" width="100%" />

# VantaWave ML

### Wi‑Fi Security • Machine Learning • MLOps • Grounded AI • SOC

[English README](README.md) · [Архитектура](docs/final_architecture.md) · [Демо](docs/demo_walkthrough.md) · [Подготовка к собеседованию](INTERVIEW_DEFENSE.md)

</div>

---

## Что это

**VantaWave ML** — это не ноутбук с одной моделью, а полноценная defensive security / ML-платформа:

```text
Wi‑Fi / PCAP / Dataset
        ↓
валидация данных
        ↓
feature engineering
        ↓
классический ML + anomaly detection
        ↓
Autoencoder / Isolation Forest
        ↓
evaluation / calibration / explainability
        ↓
Risk / Incidents
        ↓
Monitoring / Drift
        ↓
SQL persistence
        ↓
Grounded RAG Analyst
        ↓
FastAPI + SOC Dashboard
```

Проект сделан как **портфолио ML Engineer / AI Engineer / Security ML Engineer**.

---

## Что уже реализовано

- пассивное обнаружение Wi‑Fi через Windows;
- нормализованный `WirelessEvent`;
- offline PCAP replay;
- AWID3-oriented research pipeline;
- Logistic Regression / Random Forest / Histogram Gradient Boosting;
- Isolation Forest;
- PyTorch Autoencoder;
- threshold calibration;
- error analysis;
- model promotion;
- MLflow;
- SHAP;
- drift monitoring;
- retraining recommendations;
- PostgreSQL / SQLite;
- Authorized Security Lab;
- Evidence bundles;
- Capture Audit;
- Grounded AI Security Analyst;
- SOC Dashboard;
- Docker / Compose;
- **Adversary Simulation**.

---

## Adversary Simulation

<img src="docs/assets/adversary-simulation.gif" alt="Adversary simulation" width="100%" />

Это безопасный red-team слой.

Он **ничего не передаёт в эфир** и не атакует реальные сети.

Сценарии:

- deauthentication burst;
- rogue AP presence;
- authentication storm;
- retry storm;
- credential-pressure simulation.

Пример:

```powershell
python scripts/run_adversary_simulation.py deauth_burst --intensity 4
```

На выходе:

- baseline;
- synthetic attack telemetry;
- feature deltas;
- anomaly score;
- confidence;
- risk score;
- detections;
- timeline;
- JSON/Markdown report.

---

## Быстрый запуск

```powershell
git clone https://github.com/ViolettaNcl/vantawave-ml.git
cd vantawave-ml

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev,deep,pcap]"

python -m pytest
```

Демо:

```powershell
python scripts/seed_portfolio_demo.py
python scripts/build_knowledge_index.py docs
python -m uvicorn vantawave.api.main:app --reload
```

Открыть:

```text
http://127.0.0.1:8000/dashboard
```

---

## Dashboard

Разделы:

```text
Overview
Live Monitor
Wi-Fi Recovery
Capture Audit
Adversary Simulation
Incidents
Models
Experiments
Authorized Lab
Monitoring
AI Analyst
```

---

## ML / MLOps

VantaWave показывает полный lifecycle:

```text
Train
→ Validate
→ Calibrate
→ Test
→ Error Analysis
→ Promotion
→ Champion
→ Monitoring
→ Drift
→ Retraining Recommendation
```

Метрики:

- Precision
- Recall
- F1
- PR-AUC
- ROC-AUC
- FPR
- FNR
- confusion matrix
- latency

---

## Почему AI Analyst не является детектором

AI не принимает решение о том, была ли атака.

Источники истины:

- telemetry;
- ML/anomaly models;
- persisted incidents;
- evidence;
- retrieved knowledge.

AI Analyst только объясняет уже существующие данные и должен ссылаться на evidence.

---

## Исследовательская честность

Synthetic fixtures нужны для воспроизводимости.

Они **не доказывают реальную точность Wi‑Fi IDS**.

До публикации реальных метрик нужно:

1. прогнать внешний research dataset;
2. собрать разрешённую локальную telemetry;
3. провести held-out evaluation;
4. откалибровать threshold;
5. сделать error analysis;
6. сравнить domain shift.

См. [`FINAL_VALIDATION.md`](FINAL_VALIDATION.md).

---

## Безопасность

Проект ориентирован на:

- свои устройства;
- явно разрешённые lab targets;
- public research datasets;
- offline captures;
- synthetic adversary simulation.

Проект не заявляет, что может получить неизвестный WPA2/WPA3 пароль только по SSID.

Подробнее: [`SECURITY.md`](SECURITY.md).

---

## Что смотреть работодателю

- [`README.md`](README.md)
- [`docs/final_architecture.md`](docs/final_architecture.md)
- [`docs/demo_walkthrough.md`](docs/demo_walkthrough.md)
- [`INTERVIEW_DEFENSE.md`](INTERVIEW_DEFENSE.md)
- [`FINAL_VALIDATION.md`](FINAL_VALIDATION.md)

---

<div align="center">

### VantaWave ML · v1.1.0

**Production-minded ML engineering for defensive wireless security.**

</div>
