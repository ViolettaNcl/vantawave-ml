from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

from vantawave.data.awid3 import detect_label_column, load_awid3_frame
from vantawave.data.leakage import audit_feature_names
from vantawave.data.profile import profile_dataset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--label-column", default=None)
    args = parser.parse_args()

    frame = pd.read_csv(args.csv, low_memory=False)
    label_column = args.label_column or detect_label_column(frame.columns)
    profile = profile_dataset(frame, label_column=label_column)
    prepared = load_awid3_frame(frame, label_column=label_column)

    report = {
        "profile": profile.to_dict(),
        "detected_label_column": prepared.label_column,
        "usable_rows": len(prepared.features),
        "binary_distribution": {
            str(k): int(v)
            for k, v in prepared.binary_target.value_counts().to_dict().items()
        },
        "raw_attack_labels": {
            str(k): int(v)
            for k, v in prepared.raw_labels.value_counts().to_dict().items()
        },
        "feature_name_leakage_findings": [
            item.to_dict() for item in audit_feature_names(prepared.features.columns)
        ],
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
