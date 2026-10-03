import argparse
import json
from pathlib import Path
from vantawave.data.loaders import load_dataset
from vantawave.data.validation import validate_dataset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--no-target", action="store_true")
    args = parser.parse_args()

    frame = load_dataset(args.dataset)
    report = validate_dataset(frame, require_target=not args.no_target)
    print(json.dumps(report.to_dict(), indent=2))
    if not report.is_valid:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
