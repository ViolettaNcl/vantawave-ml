from __future__ import annotations

import json
from pathlib import Path

from vantawave import __version__
from vantawave.release.validation import validate_release


def main():
    checks = validate_release(Path("."))
    payload = {
        "project": "VantaWave ML",
        "version": __version__,
        "ready": all(item.ok for item in checks),
        "checks": [item.to_dict() for item in checks],
    }
    print(json.dumps(payload, indent=2))
    if not payload["ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
