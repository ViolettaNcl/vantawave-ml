from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

@dataclass(frozen=True)
class ResearchSplit:
    X_train: pd.DataFrame
    X_validation: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series

def stratified_research_split(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    random_state: int = 42,
) -> ResearchSplit:
    if len(X) != len(y):
        raise ValueError("X and y must contain the same number of rows.")
    if len(np.unique(y)) < 2:
        raise ValueError("Research split requires at least two target classes.")

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        stratify=y,
        random_state=random_state,
    )
    X_validation, X_test, y_validation, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=random_state,
    )
    return ResearchSplit(
        X_train=X_train.reset_index(drop=True),
        X_validation=X_validation.reset_index(drop=True),
        X_test=X_test.reset_index(drop=True),
        y_train=y_train.reset_index(drop=True),
        y_validation=y_validation.reset_index(drop=True),
        y_test=y_test.reset_index(drop=True),
    )
