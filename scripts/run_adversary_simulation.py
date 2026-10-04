from __future__ import annotations

import argparse
import json

from vantawave.simulation.engine import run_simulation
from vantawave.simulation.reporting import save_simulation_report
from vantawave.simulation.scenarios import list_scenarios


def main():
    parser = argparse.ArgumentParser(
        description="Run a safe synthetic adversary simulation."
    )
    parser.add_argument(
        "scenario",
        nargs="?",
        help="Scenario ID. Use --list to see options.",
    )
    parser.add_argument("--intensity", type=int, default=3)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    args = parser.parse_args()

    if args.list:
        print(json.dumps(list_scenarios(), indent=2))
        return

    if not args.scenario:
        parser.error("scenario is required unless --list is used")

    result = run_simulation(
        args.scenario,
        intensity=args.intensity,
        duration_seconds=args.duration,
        seed=args.seed,
    )
    payload = result.to_dict()

    if not args.no_save:
        json_path, md_path = save_simulation_report(
            payload,
            "artifacts/simulation/reports",
        )
        payload["report_paths"] = {
            "json": str(json_path),
            "markdown": str(md_path),
        }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
