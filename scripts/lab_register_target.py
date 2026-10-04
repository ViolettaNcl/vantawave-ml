import argparse
import json
from pathlib import Path
from vantawave.lab.registry import AuthorizedTarget, AuthorizedTargetRegistry

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--ssid", required=True)
    parser.add_argument("--bssid", required=True)
    parser.add_argument("--confirm", required=True)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--registry", type=Path, default=Path("artifacts/lab/targets.json"))
    args = parser.parse_args()

    registry = AuthorizedTargetRegistry(args.registry)
    target = registry.register(
        AuthorizedTarget(
            name=args.name,
            ssid=args.ssid,
            bssid=args.bssid,
            authorized=True,
            owner_confirmation=args.confirm,
            notes=args.notes,
        )
    )
    print(json.dumps(target.to_dict(), indent=2))

if __name__ == "__main__":
    main()
