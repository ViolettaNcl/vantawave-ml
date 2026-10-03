from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FeatureDelta:
    feature: str
    before: float
    after: float
    absolute_change: float
    percent_change: float | None

    def to_dict(self):
        return asdict(self)


def compare_feature_windows(before: dict, after: dict) -> list[FeatureDelta]:
    keys = sorted(set(before) & set(after))
    deltas = []

    for key in keys:
        before_value = before[key]
        after_value = after[key]
        if not isinstance(before_value, (int, float)):
            continue
        if not isinstance(after_value, (int, float)):
            continue

        absolute = float(after_value) - float(before_value)
        percent = None
        if abs(float(before_value)) > 1e-12:
            percent = absolute / abs(float(before_value)) * 100.0

        deltas.append(
            FeatureDelta(
                feature=key,
                before=float(before_value),
                after=float(after_value),
                absolute_change=absolute,
                percent_change=percent,
            )
        )

    return deltas
