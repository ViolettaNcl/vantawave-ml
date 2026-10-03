from __future__ import annotations

import json

from vantawave.sensors.adapters.windows_netsh import WindowsNetshSensor
from vantawave.sensors.capabilities import detect_host_capabilities


def main():
    host = detect_host_capabilities()
    windows_sensor = WindowsNetshSensor().capability()

    payload = {
        "host": host.to_dict(),
        "adapters": [
            windows_sensor.to_dict(),
            {
                "name": "pcap-replay",
                "available": host.pcap_replay,
                "mode": "offline-pcap-replay",
                "reason": None if host.pcap_replay else 'Install with: pip install -e ".[pcap]"',
            },
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
