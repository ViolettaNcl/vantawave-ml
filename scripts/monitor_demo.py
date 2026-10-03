from __future__ import annotations

import json
import numpy as np
import pandas as pd

from vantawave.db.init import initialize_database
from vantawave.db.session import create_session_factory, session_scope
from vantawave.monitoring.service import (
    evaluate_monitoring_window,
    persist_monitoring_result,
)


def main():
    rng = np.random.default_rng(42)

    reference = pd.DataFrame({
        "event_rate": rng.normal(0.5, 0.05, 200),
        "auth_rate": rng.normal(0.05, 0.01, 200),
        "channel": rng.choice(["1", "6", "11"], 200, p=[0.2, 0.6, 0.2]),
    })
    current = pd.DataFrame({
        "event_rate": rng.normal(0.8, 0.06, 100),
        "auth_rate": rng.normal(0.09, 0.015, 100),
        "channel": rng.choice(["1", "6", "11"], 100, p=[0.05, 0.2, 0.75]),
    })

    reference_scores = rng.normal(0.15, 0.03, 200)
    current_scores = rng.normal(0.28, 0.05, 100)

    result = evaluate_monitoring_window(
        reference_features=reference,
        current_features=current,
        reference_scores=reference_scores,
        current_scores=current_scores,
        performance_metrics={"f1": 0.77, "false_positive_rate": 0.12},
    )

    engine = initialize_database()
    factory = create_session_factory(engine)

    with session_scope(factory) as db:
        evaluation = persist_monitoring_result(
            db_session=db,
            result=result,
            model_name="vantawave-monitor-demo",
            dataset_name="monitor-demo",
            performance_metrics={"f1": 0.77, "false_positive_rate": 0.12},
        )
        print("evaluation_id:", evaluation.evaluation_id)

    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
