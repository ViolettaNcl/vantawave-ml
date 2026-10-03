from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import pandas as pd

from vantawave.data.awid3 import detect_label_column
from vantawave.ml.research.v05_pipeline import run_v05_research
from vantawave.mlops.mlflow_backend import (
    MLflowUnavailable,
    configure_local_mlflow,
    log_and_register_sklearn,
    promote_alias,
)
from vantawave.reports.v05 import save_v05_json, save_v05_markdown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--label-column", default=None)
    parser.add_argument("--out", type=Path, default=Path("artifacts/v05"))
    parser.add_argument("--shap", action="store_true")
    parser.add_argument("--mlflow", action="store_true")
    args = parser.parse_args()

    raw = pd.read_csv(args.csv, low_memory=False)
    label_column = args.label_column or detect_label_column(raw.columns)

    payload = run_v05_research(
        raw,
        label_column=label_column,
        output_dir=args.out,
        enable_shap=args.shap,
    )

    if args.mlflow:
        try:
            config = configure_local_mlflow(root=args.out / "mlflow")
            selected = next(
                item for item in payload["models"]
                if item["model"] == payload["selected_candidate"]
            )
            model = joblib.load(selected["artifact_path"])
            mlflow_result = log_and_register_sklearn(
                model,
                model_name=config.registry_name,
                metrics={
                    "test_f1": selected["calibrated_test"]["f1"],
                    "test_precision": selected["calibrated_test"]["precision"],
                    "test_recall": selected["calibrated_test"]["recall"],
                    "test_fpr": selected["calibrated_test"]["false_positive_rate"],
                    "test_pr_auc": selected["default_test_metrics"]["pr_auc"] or 0.0,
                },
                params={
                    "threshold": selected["threshold"]["threshold"],
                    "estimator": selected["model"],
                    "project_version": "0.5.0",
                },
                tags={
                    "dataset_family": "AWID3",
                    "task": "binary_intrusion_detection",
                },
                alias="candidate",
            )
            mlflow_promotion = None
            if payload.get("promoted_champion"):
                mlflow_promotion = promote_alias(
                    model_name=mlflow_result["model_name"],
                    version=mlflow_result["version"],
                    alias="champion",
                )

            payload["mlflow"] = {
                "status": "ok",
                "tracking_uri": config.tracking_uri,
                **mlflow_result,
                "promotion": mlflow_promotion,
            }
        except MLflowUnavailable as exc:
            payload["mlflow"] = {
                "status": "unavailable",
                "message": str(exc),
            }
    else:
        payload["mlflow"] = {"status": "not_requested"}

    json_path = save_v05_json(payload, args.out / "research_report.json")
    md_path = save_v05_markdown(payload, args.out / "research_report.md")

    print("VantaWave ML v0.5 research run")
    print("=" * 88)
    print(f"selected candidate: {payload['selected_candidate']}")
    champion = payload.get("promoted_champion")
    print(f"local champion: {champion or 'none'}")
    print("-" * 88)
    for item in payload["models"]:
        calibrated = item["calibrated_test"]
        print(
            f"{item['model']:24} "
            f"threshold={item['threshold']['threshold']:.3f} "
            f"test_f1={calibrated['f1']:.4f} "
            f"test_precision={calibrated['precision']:.4f} "
            f"test_recall={calibrated['recall']:.4f} "
            f"test_fpr={calibrated['false_positive_rate']:.4f} "
            f"promotion={'PASS' if item['promotion']['approved'] else 'FAIL'}"
        )
    print("-" * 88)
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Registry: {payload['registry_path']}")
    print(f"SHAP: {payload['shap']['status']}")
    print(f"MLflow: {payload['mlflow']['status']}")


if __name__ == "__main__":
    main()
