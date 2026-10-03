from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PromotionPolicy:
    min_test_f1: float = 0.80
    min_test_pr_auc: float = 0.85
    max_test_fpr: float = 0.10
    max_validation_test_f1_gap: float = 0.10

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class PromotionDecision:
    approved: bool
    status: str
    reasons: list[str]
    policy: PromotionPolicy

    def to_dict(self):
        return {
            "approved": self.approved,
            "status": self.status,
            "reasons": list(self.reasons),
            "policy": self.policy.to_dict(),
        }


def evaluate_promotion(
    *,
    validation_metrics: dict,
    test_metrics: dict,
    policy: PromotionPolicy | None = None,
) -> PromotionDecision:
    policy = policy or PromotionPolicy()
    reasons = []

    test_f1 = float(test_metrics.get("f1", 0.0))
    test_pr_auc = float(test_metrics.get("pr_auc") or 0.0)
    test_fpr = float(test_metrics.get("false_positive_rate", 1.0))
    validation_f1 = float(validation_metrics.get("f1", 0.0))
    gap = abs(validation_f1 - test_f1)

    if test_f1 < policy.min_test_f1:
        reasons.append(f"test_f1 {test_f1:.4f} < {policy.min_test_f1:.4f}")
    if test_pr_auc < policy.min_test_pr_auc:
        reasons.append(
            f"test_pr_auc {test_pr_auc:.4f} < {policy.min_test_pr_auc:.4f}"
        )
    if test_fpr > policy.max_test_fpr:
        reasons.append(f"test_fpr {test_fpr:.4f} > {policy.max_test_fpr:.4f}")
    if gap > policy.max_validation_test_f1_gap:
        reasons.append(
            f"validation/test F1 gap {gap:.4f} > "
            f"{policy.max_validation_test_f1_gap:.4f}"
        )

    approved = not reasons
    return PromotionDecision(
        approved=approved,
        status="approved" if approved else "rejected",
        reasons=reasons or ["All promotion checks passed."],
        policy=policy,
    )
