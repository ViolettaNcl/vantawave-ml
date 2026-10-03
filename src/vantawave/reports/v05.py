from __future__ import annotations

from pathlib import Path
import json


def save_v05_json(payload: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def save_v05_markdown(payload: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    profile = payload["dataset_profile"]
    lines = [
        "# VantaWave ML Research Report",
        "",
        f"**Project version:** {payload.get('project_version', 'unknown')}",
        f"**Experiment run:** `{payload.get('experiment_run_id', 'unknown')}`",
        f"**Dataset rows:** {profile.get('rows', 0)}",
        f"**Dataset columns:** {profile.get('columns', 0)}",
        f"**Usable research rows:** {payload.get('usable_rows', 0)}",
        f"**Label column:** `{payload.get('label_column', 'unknown')}`",
        "",
        "## Model benchmark",
        "",
        "| Model | Threshold | Val F1 | Test F1 | Test PR-AUC | Test FPR | FP | FN | Promotion |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for item in payload["models"]:
        calibrated = item["calibrated_test"]
        errors = item["error_analysis"]
        promotion = item["promotion"]
        lines.append(
            "| {model} | {threshold:.3f} | {val_f1:.4f} | {test_f1:.4f} | "
            "{pr_auc:.4f} | {fpr:.4f} | {fp} | {fn} | {promotion} |".format(
                model=item["model"],
                threshold=item["threshold"]["threshold"],
                val_f1=item["threshold"]["validation"]["f1"],
                test_f1=calibrated["f1"],
                pr_auc=float(item["default_test_metrics"].get("pr_auc") or 0.0),
                fpr=calibrated["false_positive_rate"],
                fp=errors["false_positives"],
                fn=errors["false_negatives"],
                promotion="APPROVED" if promotion["approved"] else "REJECTED",
            )
        )

    lines.extend(
        [
            "",
            "## Selected candidate",
            "",
            f"**Candidate model:** `{payload.get('selected_candidate', 'none')}`",
            f"**Promoted champion:** `{payload.get('promoted_champion') or 'none'}`",
            "",
            "## Leakage audit",
            "",
        ]
    )

    findings = payload.get("leakage_findings", [])
    if findings:
        for finding in findings:
            lines.append(
                f"- **{finding['severity'].upper()}** `{finding['column']}` — "
                f"{finding['reason']}"
            )
    else:
        lines.append("- No selected-feature leakage-name findings.")

    lines.extend(["", "## Explainability", ""])
    shap_report = payload.get("shap")
    if shap_report and shap_report.get("status") == "ok":
        lines.append(
            f"SHAP computed for `{shap_report.get('model')}`. Top transformed features:"
        )
        lines.append("")
        for item in shap_report.get("features", [])[:10]:
            lines.append(
                f"- `{item['feature']}`: mean |SHAP| = {item['mean_abs_shap']:.6f}"
            )
    else:
        lines.append(
            "SHAP was not executed in this run. Install the `explain` extra and "
            "run with `--shap` to enable it."
        )

    lines.extend(
        [
            "",
            "## Research notes",
            "",
            "- Threshold selection uses validation data only.",
            "- Final calibrated metrics are measured on the held-out test split.",
            "- Promotion is rule-based and auditable; it is not an arbitrary label.",
            "- Synthetic-fixture results are pipeline checks, not real-world IDS claims.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
