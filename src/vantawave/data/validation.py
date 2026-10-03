from dataclasses import asdict, dataclass, field
from typing import Any
import pandas as pd
from vantawave.data.schema import (
    BOUNDED_FEATURES, FEATURE_COLUMNS, NON_NEGATIVE_FEATURES, TARGET_COLUMN,
)

@dataclass
class DataQualityIssue:
    code: str
    severity: str
    message: str
    column: str | None = None
    count: int | None = None

@dataclass
class DataQualityReport:
    rows: int
    columns: int
    duplicate_rows: int
    missing_cells: int
    target_distribution: dict[str, int] = field(default_factory=dict)
    issues: list[DataQualityIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["is_valid"] = self.is_valid
        return data

def validate_dataset(frame: pd.DataFrame, *, require_target: bool = True) -> DataQualityReport:
    issues = []
    required = list(FEATURE_COLUMNS) + ([TARGET_COLUMN] if require_target else [])

    for column in [c for c in required if c not in frame.columns]:
        issues.append(DataQualityIssue("missing_column", "error",
            f"Required column '{column}' is missing.", column=column))

    duplicate_rows = int(frame.duplicated().sum())
    if duplicate_rows:
        issues.append(DataQualityIssue("duplicates", "warning",
            f"Dataset contains {duplicate_rows} duplicate rows.", count=duplicate_rows))

    missing_cells = int(frame.isna().sum().sum())
    if missing_cells:
        issues.append(DataQualityIssue("missing_values", "error",
            f"Dataset contains {missing_cells} missing cells.", count=missing_cells))

    for column in FEATURE_COLUMNS:
        if column not in frame.columns:
            continue
        if not pd.api.types.is_numeric_dtype(frame[column]):
            issues.append(DataQualityIssue("non_numeric_feature", "error",
                f"Feature '{column}' must be numeric.", column=column))
            continue
        if column in NON_NEGATIVE_FEATURES:
            count = int((frame[column] < 0).sum())
            if count:
                issues.append(DataQualityIssue("negative_value", "error",
                    f"Feature '{column}' contains negative values.", column=column, count=count))
        if column in BOUNDED_FEATURES:
            low, high = BOUNDED_FEATURES[column]
            count = int(((frame[column] < low) | (frame[column] > high)).sum())
            if count:
                issues.append(DataQualityIssue("out_of_bounds", "error",
                    f"Feature '{column}' must be between {low} and {high}.",
                    column=column, count=count))

    distribution = {}
    if TARGET_COLUMN in frame.columns:
        labels = set(frame[TARGET_COLUMN].dropna().unique().tolist())
        if not labels.issubset({0, 1}):
            issues.append(DataQualityIssue("invalid_target", "error",
                f"'{TARGET_COLUMN}' must contain only 0/1 labels.", column=TARGET_COLUMN))
        counts = frame[TARGET_COLUMN].value_counts().to_dict()
        distribution = {str(k): int(v) for k, v in counts.items()}
        if len(counts) == 2:
            minority_ratio = min(counts.values()) / max(sum(counts.values()), 1)
            if minority_ratio < 0.10:
                issues.append(DataQualityIssue("class_imbalance", "warning",
                    f"Minority class is only {minority_ratio:.1%} of labeled rows."))

    return DataQualityReport(
        rows=int(len(frame)),
        columns=int(len(frame.columns)),
        duplicate_rows=duplicate_rows,
        missing_cells=missing_cells,
        target_distribution=distribution,
        issues=issues,
    )
