from __future__ import annotations

import argparse
import json
from pathlib import Path

from vantawave.sensors.replay import replay_jsonl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("--window", type=float, default=60.0)
    args = parser.parse_args()

    payload = replay_jsonl(
        args.events,
        window_seconds=args.window,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
