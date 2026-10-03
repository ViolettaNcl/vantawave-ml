from vantawave.reports.v05 import save_v05_json, save_v05_markdown


def sample_payload():
    return {
        "project_version": "0.5.0",
        "dataset_profile": {"rows": 100, "columns": 17},
        "usable_rows": 100,
        "label_column": "Label",
        "models": [
            {
                "model": "random_forest",
                "threshold": {
                    "threshold": 0.42,
                    "validation": {
                        "f1": 0.90,
                        "false_positive_rate": 0.04,
                    },
                },
                "calibrated_test": {
                    "f1": 0.88,
                    "precision": 0.90,
                    "recall": 0.86,
                    "false_positive_rate": 0.05,
                },
                "default_test_metrics": {"pr_auc": 0.94},
                "error_analysis": {
                    "false_positives": 2,
                    "false_negatives": 3,
                },
                "promotion": {"approved": True},
            }
        ],
        "selected_candidate": "random_forest",
        "promoted_champion": {"model_name": "wifi", "version": 1},
        "leakage_findings": [],
        "shap": {"status": "not_requested", "features": []},
    }


def test_rich_report_writes_json_and_markdown(tmp_path):
    payload = sample_payload()
    json_path = save_v05_json(payload, tmp_path / "report.json")
    md_path = save_v05_markdown(payload, tmp_path / "report.md")
    assert json_path.exists()
    assert md_path.exists()
    assert "Model benchmark" in md_path.read_text(encoding="utf-8")
