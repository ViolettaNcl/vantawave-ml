from dataclasses import dataclass
import pandas as pd
from sklearn.model_selection import train_test_split
from vantawave.data.schema import TARGET_COLUMN

@dataclass(frozen=True)
class DatasetSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame

def stratified_split(
    frame: pd.DataFrame,
    *,
    target: str = TARGET_COLUMN,
    train_size: float = 0.70,
    validation_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42,
) -> DatasetSplit:
    if abs(train_size + validation_size + test_size - 1.0) > 1e-9:
        raise ValueError("Split sizes must sum to 1.0.")
    if target not in frame.columns:
        raise ValueError(f"Target column '{target}' is missing.")
    if len(frame) < 3:
        raise ValueError("Dataset is too small to create train/validation/test splits.")

    total_rows = len(frame)
    train_rows = int(round(total_rows * train_size))
    validation_rows = int(round(total_rows * validation_size))
    test_rows = total_rows - train_rows - validation_rows

    if min(train_rows, validation_rows, test_rows) <= 0:
        raise ValueError("Each split must contain at least one row.")

    train, temp = train_test_split(
        frame,
        train_size=train_rows,
        test_size=validation_rows + test_rows,
        stratify=frame[target],
        random_state=random_state,
    )
    validation, test = train_test_split(
        temp,
        train_size=validation_rows,
        test_size=test_rows,
        stratify=temp[target],
        random_state=random_state,
    )

    return DatasetSplit(
        train=train.reset_index(drop=True),
        validation=validation.reset_index(drop=True),
        test=test.reset_index(drop=True),
    )
