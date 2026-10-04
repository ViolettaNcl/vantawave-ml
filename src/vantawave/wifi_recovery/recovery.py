from __future__ import annotations


def recovery_options(*, saved_profile_exists: bool, gateway_available: bool) -> list[dict]:
    options = []

    options.append(
        {
            "id": "saved_profile",
            "title": "Windows saved profile",
            "available": saved_profile_exists,
            "description": (
                "Windows has a saved profile, so a locally authorized export can reveal "
                "the stored key."
                if saved_profile_exists
                else
                "No saved profile exists on this PC, so Windows has no stored key to reveal."
            ),
        }
    )

    options.extend(
        [
            {
                "id": "router_label",
                "title": "Router label / installation card",
                "available": True,
                "description": (
                    "Check the router label or ISP installation card for the configured "
                    "or default Wi-Fi key."
                ),
            },
            {
                "id": "isp_router_app",
                "title": "Router / ISP management app",
                "available": True,
                "description": (
                    "Use the official router or ISP app/account if it exposes Wi-Fi settings."
                ),
            },
            {
                "id": "router_admin",
                "title": "Router administration",
                "available": gateway_available,
                "description": (
                    "Use an authorized wired/admin connection to review or replace the "
                    "Wi-Fi key. Gateway detection does not bypass admin authentication."
                ),
            },
            {
                "id": "factory_reset",
                "title": "Factory reset",
                "available": True,
                "description": (
                    "As a last resort on equipment you own, reset the router and configure "
                    "a new Wi-Fi password."
                ),
            },
        ]
    )

    return options
