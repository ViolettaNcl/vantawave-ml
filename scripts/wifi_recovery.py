from __future__ import annotations

import argparse
import getpass
import json

from vantawave.wifi_recovery.recovery import recovery_options
from vantawave.wifi_recovery.strength import audit_password_strength
from vantawave.wifi_recovery.windows import (
    connect_with_password,
    current_wifi,
    delete_saved_profile,
    export_saved_key,
    gateway_info,
    list_saved_profiles,
    nearby_networks,
    profile_exists,
)


def print_json(payload):
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="VantaWave local Windows Wi-Fi recovery helper."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("profiles")
    sub.add_parser("scan")
    sub.add_parser("current")
    sub.add_parser("gateways")

    status = sub.add_parser("status")
    status.add_argument("--ssid", required=True)

    saved = sub.add_parser("saved-key")
    saved.add_argument("--ssid", required=True)
    saved.add_argument(
        "--confirm",
        action="store_true",
        help="Explicitly confirm local saved-key display.",
    )

    connect = sub.add_parser("connect")
    connect.add_argument("--ssid", required=True)
    connect.add_argument(
        "--security",
        choices=["WPA2-Personal", "WPA3-Personal"],
        default="WPA2-Personal",
    )

    delete = sub.add_parser("delete-profile")
    delete.add_argument("--ssid", required=True)

    sub.add_parser("audit-password")

    args = parser.parse_args()

    if args.command == "profiles":
        print_json({"profiles": [item.to_dict() for item in list_saved_profiles()]})
        return

    if args.command == "scan":
        print_json({"networks": nearby_networks()})
        return

    if args.command == "current":
        print_json(current_wifi().to_dict())
        return

    if args.command == "gateways":
        print_json({"gateways": [item.to_dict() for item in gateway_info()]})
        return

    if args.command == "status":
        saved_profile = profile_exists(args.ssid)
        gateways = gateway_info()
        print_json(
            {
                "ssid": args.ssid,
                "saved_profile": saved_profile,
                "unknown_password_derivable": False,
                "recovery_options": recovery_options(
                    saved_profile_exists=saved_profile,
                    gateway_available=bool(gateways),
                ),
            }
        )
        return

    if args.command == "saved-key":
        if not args.confirm:
            raise SystemExit(
                "Use --confirm to explicitly request display of a locally saved Windows Wi-Fi key."
            )
        key = export_saved_key(args.ssid, allow_secret=True)
        if key is None:
            print("No saved Windows key exists for this SSID on this laptop.")
        else:
            print(key)
        return

    if args.command == "connect":
        password = getpass.getpass("Wi-Fi password (input hidden): ")
        print_json(
            connect_with_password(
                args.ssid,
                password,
                security=args.security,
            )
        )
        return

    if args.command == "delete-profile":
        print_json(delete_saved_profile(args.ssid))
        return

    if args.command == "audit-password":
        password = getpass.getpass("Password to audit locally (input hidden): ")
        print_json(audit_password_strength(password).to_dict())
        return


if __name__ == "__main__":
    main()
