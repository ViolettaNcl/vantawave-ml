from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np


@dataclass(frozen=True)
class ErrorCase:
    index: int
    truth: int
    prediction: int
    score: float
    error_type: str

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ErrorAnalysis:
    total_rows: int
    false_positives: int
    false_negatives: int
    correct: int
    top_false_positives: list[ErrorCase]
    top_false_negatives: list[ErrorCase]

    def to_dict(self):
        return {
            "total_rows": self.total_rows,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "correct": self.correct,
            "top_false_positives": [x.to_dict() for x in self.top_false_positives],
            "top_false_negatives": [x.to_dict() for x in self.top_false_negatives],
        }


def analyze_errors(
    y_true,
    scores,
    *,
    threshold: float,
    top_n: int = 10,
) -> ErrorAnalysis:
    truth = np.asarray(y_true, dtype=int)
    scores = np.asarray(scores, dtype=float)
    prediction = (scores >= threshold).astype(int)

    fp_idx = np.where((truth == 0) & (prediction == 1))[0]
    fn_idx = np.where((truth == 1) & (prediction == 0))[0]

    fp_sorted = fp_idx[np.argsort(scores[fp_idx])[::-1]] if len(fp_idx) else fp_idx
    fn_sorted = fn_idx[np.argsort(scores[fn_idx])] if len(fn_idx) else fn_idx

    def cases(indices, error_type):
        items = []
        for idx in indices[:top_n]:
            items.append(
                ErrorCase(
                    index=int(idx),
                    truth=int(truth[idx]),
                    prediction=int(prediction[idx]),
                    score=float(scores[idx]),
                    error_type=error_type,
                )
            )
        return items

    return ErrorAnalysis(
        total_rows=int(len(truth)),
        false_positives=int(len(fp_idx)),
        false_negatives=int(len(fn_idx)),
        correct=int((prediction == truth).sum()),
        top_false_positives=cases(fp_sorted, "false_positive"),
        top_false_negatives=cases(fn_sorted, "false_negative"),
    )
