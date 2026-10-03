from __future__ import annotations

from pathlib import Path
import json


def save_v06_json(payload: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def save_v06_markdown(payload: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    auto = payload["autoencoder"]
    iso = payload["isolation_forest"]
    comp = payload["comparison"]

    lines = [
        "# VantaWave ML v0.6 — Deep Anomaly Detection Report",
        "",
        f"**Task:** `{payload['task']}`",
        f"**Known attack labels:** {', '.join(payload['known_attack_labels']) or 'none'}",
        f"**Transformed feature count:** {payload['transformed_feature_count']}",
        "",
        "## Split",
        "",
        f"- Train normal: {payload['split']['train_normal']}",
        f"- Validation normal: {payload['split']['validation_normal']}",
        f"- Test normal: {payload['split']['test_normal']}",
        f"- Test anomalies: {payload['split']['test_anomalies']}",
        "",
        "## Model comparison",
        "",
        "| Model | F1 | Precision | Recall | FPR | PR-AUC | ROC-AUC | Unknown recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        "| Autoencoder | {f1:.4f} | {precision:.4f} | {recall:.4f} | {fpr:.4f} | "
        "{pr_auc:.4f} | {roc_auc:.4f} | {unknown} |".format(
            f1=auto["metrics"]["f1"],
            precision=auto["metrics"]["precision"],
            recall=auto["metrics"]["recall"],
            fpr=auto["metrics"]["false_positive_rate"],
            pr_auc=auto["metrics"]["pr_auc"],
            roc_auc=auto["metrics"]["roc_auc"],
            unknown=(
                f"{auto['attack_recall']['unknown_attacks']['recall']:.4f}"
                if auto["attack_recall"]["unknown_attacks"]["recall"] is not None
                else "n/a"
            ),
        ),
        "| Isolation Forest | {f1:.4f} | {precision:.4f} | {recall:.4f} | {fpr:.4f} | "
        "{pr_auc:.4f} | {roc_auc:.4f} | {unknown} |".format(
            f1=iso["metrics"]["f1"],
            precision=iso["metrics"]["precision"],
            recall=iso["metrics"]["recall"],
            fpr=iso["metrics"]["false_positive_rate"],
            pr_auc=iso["metrics"]["pr_auc"],
            roc_auc=iso["metrics"]["roc_auc"],
            unknown=(
                f"{iso['attack_recall']['unknown_attacks']['recall']:.4f}"
                if iso["attack_recall"]["unknown_attacks"]["recall"] is not None
                else "n/a"
            ),
        ),
        "",
        "## Autoencoder training",
        "",
        f"- Device: `{auto['device']}`",
        f"- Best epoch: {auto['training']['best_epoch']}",
        f"- Best validation loss: {auto['training']['best_validation_loss']:.8f}",
        f"- Threshold method: `{auto['threshold_method']}`",
        f"- Threshold: {auto['threshold']:.8f}",
        "",
        "## Attack recall",
        "",
    ]

    for label, item in auto["attack_recall"]["by_attack_label"].items():
        lines.append(
            f"- `{label}` ({item['category']}): rows={item['rows']}, recall={item['recall']:.4f}"
        )

    lines.extend(
        [
            "",
            "## Drift baseline",
            "",
            f"- Baseline path: `{payload['drift']['baseline_path']}`",
            f"- Current drift warnings: {payload['drift']['warning_count']}",
            f"- Current high-severity drift findings: {payload['drift']['high_count']}",
            "",
            "## Notes",
            "",
            "- The autoencoder is trained only on normal traffic.",
            "- The anomaly threshold is calibrated only from normal validation reconstruction error.",
            "- Attack rows are never used to train the autoencoder.",
            "- Known/unknown categories are evaluation groupings, not training labels.",
            "- Synthetic fixture results are pipeline checks, not real-world IDS claims.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
