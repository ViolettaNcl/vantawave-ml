from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

from vantawave.data.awid3 import detect_label_column, load_awid3_frame
from vantawave.data.leakage import audit_feature_names
from vantawave.data.profile import profile_dataset
from vantawave.ml.research.benchmark import run_awid3_benchmark
from vantawave.ml.research.splitting import stratified_research_split
from vantawave.reports.research import save_research_report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--label-column", default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/awid3"),
    )
    args = parser.parse_args()

    raw = pd.read_csv(args.csv, low_memory=False)
    label_column = args.label_column or detect_label_column(raw.columns)
    profile = profile_dataset(raw, label_column=label_column)
    prepared = load_awid3_frame(raw, label_column=label_column)

    leakage = audit_feature_names(prepared.features.columns)
    if any(item.severity == "error" for item in leakage):
        raise SystemExit(
            "Potential target leakage detected in selected feature names. "
            "Review the report before training."
        )

    split = stratified_research_split(
        prepared.features,
        prepared.binary_target,
    )

    evaluations, importance, best_model = run_awid3_benchmark(
        split,
        artifact_dir=args.out / "models",
    )

    report_path = save_research_report(
        dataset_profile=profile.to_dict(),
        leakage_findings=[item.to_dict() for item in leakage],
        evaluations=evaluations,
        feature_importance=[item.to_dict() for item in importance],
        output=args.out / "research_report.json",
    )

    print("VantaWave ML — AWID3 research benchmark")
    print("=" * 88)
    print(f"usable rows: {len(prepared.features)}")
    print(f"label column: {prepared.label_column}")
    print(f"best validation model: {best_model}")
    print("-" * 88)
    for item in evaluations:
        print(
            f"{item.model:24} "
            f"val_f1={item.validation['f1']:.4f} "
            f"test_f1={item.test['f1']:.4f} "
            f"test_pr_auc={(item.test['pr_auc'] or 0):.4f} "
            f"test_fpr={item.test['false_positive_rate']:.4f}"
        )
    print("-" * 88)
    print("Top permutation features:")
    for item in importance[:8]:
        print(f"  {item.feature:36} {item.importance_mean:+.6f}")
    print(f"report: {report_path}")

if __name__ == "__main__":
    main()
