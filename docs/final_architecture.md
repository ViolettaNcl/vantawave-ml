# VantaWave ML v1.0 — Final Architecture

```mermaid
flowchart TD
    A[Windows WLAN / Offline PCAP / Research Dataset] --> B[Sensor Adapters]
    B --> C[Normalized WirelessEvent]
    C --> D[Rolling Feature Windows]
    D --> E1[Classical ML]
    D --> E2[Isolation Forest]
    D --> E3[PyTorch Autoencoder]

    E1 --> F[Evaluation + Threshold Calibration]
    E2 --> F
    E3 --> F

    F --> G[Model Registry + MLflow + SHAP]
    F --> H[Risk / Incident Engine]

    H --> I[Authorized Lab Evidence]
    H --> J[Persistent SQL Data Layer]
    I --> J

    J --> K[Feature Drift + Score Drift]
    K --> L[Retraining Recommendation]

    J --> M[Historical Incident Retrieval]
    N[Project Knowledge Base] --> O[RAG Retriever]
    M --> P[Grounded Security Analyst]
    O --> P

    P --> Q[FastAPI]
    L --> Q
    J --> Q
    B --> Q

    Q --> R[SOC Dashboard]
    Q --> S[Swagger API]
    Q --> T[Docker / PostgreSQL Runtime]
```

## Layer boundaries

### Collection
Hardware/OS-specific sensor code emits normalized events.

### Feature engineering
Time-window aggregation transforms events into measurable features.

### ML
Supervised models and anomaly models remain independent from sensor drivers.

### Evaluation
Threshold selection, model promotion, error analysis, explainability and
registry logic are explicit and auditable.

### Persistence
SQLAlchemy models store targets, sessions, incidents, drift, model snapshots
and evaluation history.

### AI
The Security Analyst reads persisted evidence plus retrieved documentation.
It does not generate source evidence itself.

### UI
The dashboard consumes public API endpoints. It does not contain duplicate ML
or database business logic.
