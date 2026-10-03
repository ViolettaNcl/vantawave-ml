from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pandas as pd

# Expert-selected IEEE 802.11 features commonly used in AWID2/AWID3 research.
AWID3_NUMERIC_FEATURES = [
    "frame.len",
    "radiotap.length",
    "radiotap.dbm_antsignal",
    "wlan.duration",
]

AWID3_CATEGORICAL_FEATURES = [
    "radiotap.present.tsft",
    "radiotap.channel.freq",
    "radiotap.channel.type.cck",
    "radiotap.channel.type.ofdm",
    "wlan.fc.type",
    "wlan.fc.subtype",
    "wlan.fc.ds",
    "wlan.fc.frag",
    "wlan.fc.retry",
    "wlan.fc.pwrmgt",
    "wlan.fc.moredata",
    "wlan.fc.protected",
]

AWID3_FEATURES = AWID3_NUMERIC_FEATURES + AWID3_CATEGORICAL_FEATURES

# Public AWID3 CSVs and papers use small naming variations across exports.
COLUMN_ALIASES = {
    "radiotap.len": "radiotap.length",
    "radiotap.channel.flags.cck": "radiotap.channel.type.cck",
    "radiotap.channel.flags.ofdm": "radiotap.channel.type.ofdm",
    "radiotap.channel.type.cck": "radiotap.channel.type.cck",
    "radiotap.channel.type.ofdm": "radiotap.channel.type.ofdm",
}

LABEL_CANDIDATES = [
    "Label",
    "label",
    "attack_map",
    "attack",
    "class",
    "Class",
]

NORMAL_LABELS = {
    "normal",
    "benign",
    "0",
    "no attack",
    "no_attack",
}

@dataclass(frozen=True)
class Awid3Dataset:
    features: pd.DataFrame
    binary_target: pd.Series
    raw_labels: pd.Series
    label_column: str

def normalize_awid3_columns(frame: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for column in frame.columns:
        stripped = str(column).strip()
        canonical = COLUMN_ALIASES.get(stripped, stripped)
        if canonical != column:
            rename[column] = canonical
    return frame.rename(columns=rename)

def detect_label_column(columns: Iterable[str]) -> str:
    available = set(columns)
    for candidate in LABEL_CANDIDATES:
        if candidate in available:
            return candidate
    raise ValueError(
        "Could not detect AWID3 label column. Expected one of: "
        + ", ".join(LABEL_CANDIDATES)
    )

def _clean_string_series(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .replace({"?": pd.NA, "": pd.NA, "nan": pd.NA, "None": pd.NA})
    )

def load_awid3_frame(
    frame: pd.DataFrame,
    *,
    label_column: str | None = None,
    drop_missing: bool = True,
) -> Awid3Dataset:
    frame = normalize_awid3_columns(frame).copy()
    label_column = label_column or detect_label_column(frame.columns)

    missing_features = [name for name in AWID3_FEATURES if name not in frame.columns]
    if missing_features:
        raise ValueError(
            "AWID3 input is missing required research features: "
            + ", ".join(missing_features)
        )

    selected = frame[AWID3_FEATURES + [label_column]].copy()

    for column in AWID3_NUMERIC_FEATURES:
        selected[column] = pd.to_numeric(selected[column], errors="coerce")

    for column in AWID3_CATEGORICAL_FEATURES:
        selected[column] = _clean_string_series(selected[column])

    selected[label_column] = _clean_string_series(selected[label_column])

    if drop_missing:
        selected = selected.dropna().reset_index(drop=True)

    if selected.empty:
        raise ValueError("No usable AWID3 rows remain after preprocessing.")

    raw_labels = selected[label_column].astype("string")
    binary_target = raw_labels.str.lower().map(
        lambda value: 0 if value in NORMAL_LABELS else 1
    ).astype(int)

    return Awid3Dataset(
        features=selected[AWID3_FEATURES].copy(),
        binary_target=binary_target.rename("is_anomaly"),
        raw_labels=raw_labels.rename("attack_label"),
        label_column=label_column,
    )
