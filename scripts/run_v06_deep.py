from __future__ import annotations

import argparse
from pathlib import Path
import json
import pandas as pd

from vantawave.data.awid3 import detect_label_column, load_awid3_frame
from vantawave.ml.deep.pipeline import run_deep_anomaly_research, make_normal_only_split
from vantawave.ml.drift.baseline import build_drift_baseline, compare_to_baseline
from vantawave.reports.v06 import save_v06_json, save_v06_markdown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--label-column", default=None)
    parser.add_argument("--out", type=Path, default=Path("artifacts/v06"))
    parser.add_argument(
        "--known-attack",
        action="append",
        default=["Deauth"],
        help="Attack label treated as known for grouped evaluation. Repeatable.",
    )
    args = parser.parse_args()

    raw = pd.read_csv(args.csv, low_memory=False)
    label_column = args.label_column or detect_label_column(raw.columns)

    payload = run_deep_anomaly_research(
        raw,
        label_column=label_column,
        output_dir=args.out,
        known_attack_labels=set(args.known_attack),
    )

    prepared = load_awid3_frame(raw, label_column=label_column)
    split = make_normal_only_split(
        prepared.features,
        prepared.binary_target,
        prepared.raw_labels,
    )

    baseline = build_drift_baseline(split.train_normal)
    baseline_path = args.out / "drift_baseline.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")

    drift_findings = compare_to_baseline(baseline, split.test_normal)
    payload["drift"] = {
        "baseline_path": str(baseline_path),
        "warning_count": sum(item.severity == "warning" for item in drift_findings),
        "high_count": sum(item.severity == "high" for item in drift_findings),
        "findings": [item.to_dict() for item in drift_findings],
    }

    json_path = save_v06_json(payload, args.out / "deep_anomaly_report.json")
    md_path = save_v06_markdown(payload, args.out / "deep_anomaly_report.md")

    print("VantaWave ML v0.6 — Deep Anomaly Detection")
    print("=" * 92)
    print(
        f"Autoencoder: f1={payload['autoencoder']['metrics']['f1']:.4f} "
        f"recall={payload['autoencoder']['metrics']['recall']:.4f} "
        f"fpr={payload['autoencoder']['metrics']['false_positive_rate']:.4f}"
    )
    print(
        f"IsolationForest: f1={payload['isolation_forest']['metrics']['f1']:.4f} "
        f"recall={payload['isolation_forest']['metrics']['recall']:.4f} "
        f"fpr={payload['isolation_forest']['metrics']['false_positive_rate']:.4f}"
    )
    print("-" * 92)
    print("Autoencoder attack recall:")
    for label, item in payload["autoencoder"]["attack_recall"]["by_attack_label"].items():
        print(
            f"  {label:16} category={item['category']:7} "
            f"rows={item['rows']:3d} recall={item['recall']:.4f}"
        )
    print("-" * 92)
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Drift baseline: {baseline_path}")


if __name__ == "__main__":
    main()
