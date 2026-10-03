from __future__ import annotations
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass(frozen=True)
class DatasetProfile:
    rows: int
    columns: int
    numeric_columns: int
    categorical_columns: int
    missing_cells: int
    duplicate_rows: int
    memory_bytes: int
    label_distribution: dict[str, int]

    def to_dict(self):
        return asdict(self)

def profile_dataset(frame: pd.DataFrame, label_column: str | None = None) -> DatasetProfile:
    numeric = frame.select_dtypes(include="number")
    distribution = {}
    if label_column and label_column in frame.columns:
        counts = frame[label_column].astype("string").value_counts(dropna=False)
        distribution = {str(k): int(v) for k, v in counts.items()}

    return DatasetProfile(
        rows=int(len(frame)),
        columns=int(len(frame.columns)),
        numeric_columns=int(len(numeric.columns)),
        categorical_columns=int(len(frame.columns) - len(numeric.columns)),
        missing_cells=int(frame.isna().sum().sum()),
        duplicate_rows=int(frame.duplicated().sum()),
        memory_bytes=int(frame.memory_usage(deep=True).sum()),
        label_distribution=distribution,
    )
