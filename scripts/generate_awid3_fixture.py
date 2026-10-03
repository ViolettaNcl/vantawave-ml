from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data/demo/awid3_fixture.csv")


def make_rows(rng, n: int, label: str):
    if label == "Normal":
        frame_len = rng.normal(520, 180, n).clip(70, 1500)
        signal = rng.normal(-155, 20, n)
        duration = rng.normal(65, 35, n).clip(0)
        retry = rng.choice(["0", "1"], n, p=[0.94, 0.06])
        protected = rng.choice(["0", "1"], n, p=[0.08, 0.92])
        subtype = rng.choice(["0", "4", "8"], n)
        freq = rng.choice(["2412", "2437", "2462", "5180"], n)
    elif label == "Deauth":
        frame_len = rng.normal(120, 25, n).clip(70, 500)
        signal = rng.normal(-130, 18, n)
        duration = rng.normal(210, 80, n).clip(0)
        retry = rng.choice(["0", "1"], n, p=[0.55, 0.45])
        protected = rng.choice(["0", "1"], n, p=[0.7, 0.3])
        subtype = rng.choice(["10", "11", "12"], n)
        freq = rng.choice(["2412", "2437"], n)
    elif label == "RogueAP":
        frame_len = rng.normal(350, 110, n).clip(70, 1100)
        signal = rng.normal(-105, 12, n)
        duration = rng.normal(130, 55, n).clip(0)
        retry = rng.choice(["0", "1"], n, p=[0.75, 0.25])
        protected = rng.choice(["0", "1"], n, p=[0.45, 0.55])
        subtype = rng.choice(["8", "5", "4"], n)
        freq = rng.choice(["2412", "2462", "5180"], n)
    elif label == "Flood":
        frame_len = rng.normal(220, 75, n).clip(70, 900)
        signal = rng.normal(-118, 16, n)
        duration = rng.normal(320, 100, n).clip(0)
        retry = rng.choice(["0", "1"], n, p=[0.35, 0.65])
        protected = rng.choice(["0", "1"], n, p=[0.6, 0.4])
        subtype = rng.choice(["11", "12", "13"], n)
        freq = rng.choice(["2412", "2437", "2462"], n)
    else:
        raise ValueError(label)

    return pd.DataFrame(
        {
            "frame.len": frame_len,
            "radiotap.length": rng.choice([48, 56, 64], n),
            "radiotap.dbm_antsignal": signal,
            "wlan.duration": duration,
            "radiotap.present.tsft": rng.choice(["0-0-0", "1-0-0"], n),
            "radiotap.channel.freq": freq,
            "radiotap.channel.type.cck": rng.choice(["0", "1"], n),
            "radiotap.channel.type.ofdm": rng.choice(["0", "1"], n),
            "wlan.fc.type": rng.choice(["0", "1", "2"], n),
            "wlan.fc.subtype": subtype,
            "wlan.fc.ds": rng.choice(["0", "1", "2", "3"], n),
            "wlan.fc.frag": rng.choice(["0", "1"], n, p=[0.98, 0.02]),
            "wlan.fc.retry": retry,
            "wlan.fc.pwrmgt": rng.choice(["0", "1"], n),
            "wlan.fc.moredata": rng.choice(["0", "1"], n),
            "wlan.fc.protected": protected,
            "Label": label,
        }
    )


def main():
    rng = np.random.default_rng(42)
    frame = pd.concat(
        [
            make_rows(rng, 900, "Normal"),
            make_rows(rng, 50, "Deauth"),
            make_rows(rng, 30, "RogueAP"),
            make_rows(rng, 20, "Flood"),
        ],
        ignore_index=True,
    ).sample(frac=1, random_state=42).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(f"Created AWID3-shaped synthetic fixture: {OUT}")
    print(frame["Label"].value_counts())


if __name__ == "__main__":
    main()
