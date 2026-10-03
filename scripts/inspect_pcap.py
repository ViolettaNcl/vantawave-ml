from __future__ import annotations

import argparse
import json
from pathlib import Path

from vantawave.sensors.features.window import aggregate_events
from vantawave.sensors.pcap.replay import PcapReplaySensor


def main():
    parser = argparse.ArgumentParser(
        description="Offline 802.11 PCAP/PCAPNG replay. No live capture or packet injection."
    )
    parser.add_argument("pcap", type=Path)
    parser.add_argument("--window", type=float, default=None)
    args = parser.parse_args()

    sensor = PcapReplaySensor(args.pcap)
    events = sensor.collect_once()

    payload = {
        "pcap": str(args.pcap),
        "events": len(events),
        "event_types": {},
        "features": None,
    }

    for event in events:
        key = event.event_type.value
        payload["event_types"][key] = payload["event_types"].get(key, 0) + 1

    if events:
        features = aggregate_events(
            events,
            duration_seconds=args.window,
        )
        payload["features"] = features.to_dict()
        payload["legacy_features"] = features.to_legacy_feature_row()

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
