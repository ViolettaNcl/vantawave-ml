from __future__ import annotations

from pathlib import Path
import joblib

from vantawave.data.awid3 import load_awid3_frame
from vantawave.data.leakage import audit_feature_names
from vantawave.data.profile import profile_dataset
from vantawave.experiments.store import ExperimentRun, FileExperimentStore
from vantawave.ml.calibration.thresholds import (
    calibrate_threshold,
    positive_scores,
    score_threshold,
)
from vantawave.ml.error_analysis.analyzer import analyze_errors
from vantawave.ml.evaluation.metrics import evaluate_binary_classifier
from vantawave.ml.explainability.permutation import permutation_feature_importance
from vantawave.ml.explainability.shap_explainer import (
    SHAPUnavailable,
    explain_tree_pipeline,
)
from vantawave.ml.promotion.policy import PromotionPolicy, evaluate_promotion
from vantawave.ml.research.models import build_awid3_models
from vantawave.ml.research.splitting import stratified_research_split
from vantawave.registry.local import LocalModelRegistry


def run_v05_research(
    raw_frame,
    *,
    label_column: str | None = None,
    output_dir: str | Path = "artifacts/v05",
    enable_shap: bool = False,
    promotion_policy: PromotionPolicy | None = None,
) -> dict:
    output_dir = Path(output_dir)
    model_dir = output_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    prepared = load_awid3_frame(raw_frame, label_column=label_column)
    profile = profile_dataset(raw_frame, label_column=prepared.label_column)
    leakage = audit_feature_names(prepared.features.columns)

    if any(item.severity == "error" for item in leakage):
        raise ValueError("Selected research features failed the leakage audit.")

    split = stratified_research_split(
        prepared.features,
        prepared.binary_target,
    )

    registry = LocalModelRegistry(output_dir / "registry")
    experiment_store = FileExperimentStore(output_dir / "experiments")
    experiment = ExperimentRun(
        name="awid3-binary-research",
        version="0.5.0",
        params={
            "split": "70/15/15",
            "threshold_objective": "f1",
            "threshold_min_precision": 0.60,
            "threshold_max_fpr": 0.20,
        },
        metrics={},
        dataset={
            "rows": profile.rows,
            "columns": profile.columns,
            "label_column": prepared.label_column,
            "usable_rows": int(len(prepared.features)),
        },
        tags={
            "dataset_family": "AWID3",
            "task": "binary_intrusion_detection",
        },
    )

    policy = promotion_policy or PromotionPolicy()
    model_reports = []
    fitted_models = {}

    for model_name, model in build_awid3_models().items():
        model.fit(split.X_train, split.y_train)
        fitted_models[model_name] = model

        default_validation = evaluate_binary_classifier(
            model, split.X_validation, split.y_validation
        ).to_dict()
        default_test = evaluate_binary_classifier(
            model, split.X_test, split.y_test
        ).to_dict()

        validation_scores = positive_scores(model, split.X_validation)
        calibration = calibrate_threshold(
            split.y_validation,
            validation_scores,
            objective="f1",
            min_precision=0.60,
            max_false_positive_rate=0.20,
        )

        test_scores = positive_scores(model, split.X_test)
        calibrated_test = score_threshold(
            split.y_test,
            test_scores,
            calibration.threshold,
        )
        errors = analyze_errors(
            split.y_test,
            test_scores,
            threshold=calibration.threshold,
        )

        promotion_metrics = {
            **default_test,
            "f1": calibrated_test.f1,
            "precision": calibrated_test.precision,
            "recall": calibrated_test.recall,
            "false_positive_rate": calibrated_test.false_positive_rate,
        }
        validation_for_promotion = {
            **default_validation,
            "f1": calibration.validation.f1,
        }
        promotion = evaluate_promotion(
            validation_metrics=validation_for_promotion,
            test_metrics=promotion_metrics,
            policy=policy,
        )

        model_path = model_dir / f"{model_name}.joblib"
        joblib.dump(model, model_path)

        registry_entry = registry.register(
            model_name="vantawave-awid3-binary",
            artifact_path=model_path,
            metrics=promotion_metrics,
            threshold=calibration.threshold,
            metadata={
                "estimator": model_name,
                "project_version": "0.5.0",
                "promotion_approved": promotion.approved,
                "experiment_run_id": experiment.run_id,
            },
        )

        model_reports.append(
            {
                "model": model_name,
                "artifact_path": str(model_path),
                "registry": registry_entry.to_dict(),
                "default_validation_metrics": default_validation,
                "default_test_metrics": default_test,
                "threshold": calibration.to_dict(),
                "calibrated_test": calibrated_test.to_dict(),
                "error_analysis": errors.to_dict(),
                "promotion": promotion.to_dict(),
            }
        )

    selected = max(
        model_reports,
        key=lambda item: (
            item["threshold"]["validation"]["f1"],
            -item["threshold"]["validation"]["false_positive_rate"],
        ),
    )

    promoted = None
    if selected["promotion"]["approved"]:
        promoted = registry.promote_to_champion(
            "vantawave-awid3-binary",
            selected["registry"]["version"],
        )

    best_model_name = selected["model"]
    best_model = fitted_models[best_model_name]

    permutation = permutation_feature_importance(
        best_model,
        split.X_test,
        split.y_test,
        scoring="f1",
        repeats=3,
    )

    shap_payload = {
        "status": "not_requested",
        "model": best_model_name,
        "features": [],
    }
    if enable_shap:
        if best_model_name != "random_forest":
            # SHAP TreeExplainer is intentionally restricted here to the tree pipeline.
            tree_model = fitted_models.get("random_forest")
            shap_model_name = "random_forest"
        else:
            tree_model = best_model
            shap_model_name = best_model_name

        try:
            features = explain_tree_pipeline(
                tree_model,
                split.X_test,
                max_rows=300,
                top_n=20,
            )
            shap_payload = {
                "status": "ok",
                "model": shap_model_name,
                "features": [item.to_dict() for item in features],
            }
        except SHAPUnavailable as exc:
            shap_payload = {
                "status": "unavailable",
                "model": shap_model_name,
                "message": str(exc),
                "features": [],
            }

    experiment.metrics = {
        item["model"]: {
            "validation_f1": item["threshold"]["validation"]["f1"],
            "test_f1": item["calibrated_test"]["f1"],
            "test_pr_auc": item["default_test_metrics"]["pr_auc"],
            "test_fpr": item["calibrated_test"]["false_positive_rate"],
        }
        for item in model_reports
    }
    experiment.artifacts = {
        "models_dir": str(model_dir),
        "registry": str(registry.manifest),
    }
    experiment_path = experiment_store.save(experiment)

    return {
        "project_version": "0.5.0",
        "experiment_run_id": experiment.run_id,
        "experiment_path": str(experiment_path),
        "dataset_profile": profile.to_dict(),
        "usable_rows": int(len(prepared.features)),
        "label_column": prepared.label_column,
        "label_distribution": {
            str(k): int(v)
            for k, v in prepared.raw_labels.value_counts().to_dict().items()
        },
        "leakage_findings": [item.to_dict() for item in leakage],
        "models": model_reports,
        "selected_candidate": best_model_name,
        "promoted_champion": (
            {
                "model_name": promoted["model_name"],
                "version": promoted["version"],
                "model_id": promoted["model_id"],
            }
            if promoted
            else None
        ),
        "permutation_importance": [item.to_dict() for item in permutation[:20]],
        "shap": shap_payload,
        "promotion_policy": policy.to_dict(),
        "registry_path": str(registry.manifest),
    }
