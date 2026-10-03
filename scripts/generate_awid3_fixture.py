from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from vantawave.data.awid3 import AWID3_FEATURES

OUT = Path("data/demo/awid3_fixture.csv")

def main():
    rng = np.random.default_rng(42)
    normal_n = 900
    attack_n = 100

    def make_rows(n: int, attack: bool):
        if attack:
            frame_len = rng.normal(120, 25, n).clip(70, 500)
            signal = rng.normal(-130, 18, n)
            duration = rng.normal(210, 80, n).clip(0)
            retry = rng.choice(["0", "1"], n, p=[0.55, 0.45])
            protected = rng.choice(["0", "1"], n, p=[0.7, 0.3])
            subtype = rng.choice(["10", "11", "12"], n)
        else:
            frame_len = rng.normal(520, 180, n).clip(70, 1500)
            signal = rng.normal(-155, 20, n)
            duration = rng.normal(65, 35, n).clip(0)
            retry = rng.choice(["0", "1"], n, p=[0.94, 0.06])
            protected = rng.choice(["0", "1"], n, p=[0.08, 0.92])
            subtype = rng.choice(["0", "4", "8"], n)

        return pd.DataFrame(
            {
                "frame.len": frame_len,
                "radiotap.length": rng.choice([48, 56, 64], n),
                "radiotap.dbm_antsignal": signal,
                "wlan.duration": duration,
                "radiotap.present.tsft": rng.choice(["0-0-0", "1-0-0"], n),
                "radiotap.channel.freq": rng.choice(["2412", "2437", "2462", "5180"], n),
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
                "Label": "Deauth" if attack else "Normal",
            }
        )

    frame = pd.concat(
        [make_rows(normal_n, False), make_rows(attack_n, True)],
        ignore_index=True,
    ).sample(frac=1, random_state=42).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(f"Created AWID3-shaped synthetic fixture: {OUT}")
    print(frame["Label"].value_counts())

if __name__ == "__main__":
    main()
