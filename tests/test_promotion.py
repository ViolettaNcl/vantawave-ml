from vantawave.ml.promotion.policy import PromotionPolicy, evaluate_promotion


def test_promotion_approved_when_policy_passes():
    decision = evaluate_promotion(
        validation_metrics={"f1": 0.91},
        test_metrics={
            "f1": 0.89,
            "pr_auc": 0.94,
            "false_positive_rate": 0.04,
        },
    )
    assert decision.approved
    assert decision.status == "approved"


def test_promotion_rejected_when_fpr_too_high():
    policy = PromotionPolicy(max_test_fpr=0.05)
    decision = evaluate_promotion(
        validation_metrics={"f1": 0.90},
        test_metrics={
            "f1": 0.88,
            "pr_auc": 0.93,
            "false_positive_rate": 0.20,
        },
        policy=policy,
    )
    assert not decision.approved
    assert any("test_fpr" in reason for reason in decision.reasons)
