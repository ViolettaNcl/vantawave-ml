import argparse
from pathlib import Path
from vantawave.data.loaders import load_dataset
from vantawave.data.splitting import stratified_split
from vantawave.data.validation import validate_dataset
from vantawave.ml.benchmark import run_benchmark, save_benchmark_report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/benchmark"))
    args = parser.parse_args()

    frame = load_dataset(args.dataset)
    quality = validate_dataset(frame)
    if not quality.is_valid:
        raise SystemExit("Dataset failed validation. Run validate_dataset.py for details.")

    split = stratified_split(frame)
    entries = run_benchmark(
        split.train,
        split.validation,
        artifact_dir=args.artifacts / "models",
    )
    report_path = args.artifacts / "benchmark.json"
    save_benchmark_report(entries, report_path)

    print("VantaWave ML model benchmark")
    print("-" * 92)
    print(f"{'model':28} {'precision':>10} {'recall':>10} {'f1':>10} {'pr_auc':>10} {'fpr':>10}")
    for entry in entries:
        m = entry.metrics
        print(
            f"{entry.model:28} "
            f"{m.precision:10.4f} {m.recall:10.4f} {m.f1:10.4f} "
            f"{(m.pr_auc or 0):10.4f} {m.false_positive_rate:10.4f}"
        )
    print("-" * 92)
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
