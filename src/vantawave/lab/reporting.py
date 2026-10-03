from __future__ import annotations

from pathlib import Path
import json


def save_lab_report(payload: dict, output_dir: str | Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "lab_report.json"
    md_path = output_dir / "lab_report.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# VantaWave Authorized Lab Report",
        "",
        f"**Session:** `{payload['session']['session_id']}`",
        f"**Target:** `{payload['target']['name']}`",
        f"**SSID:** `{payload['target']['ssid']}`",
        f"**BSSID:** `{payload['target']['bssid']}`",
        f"**Mode:** `{payload['session']['mode']}`",
        f"**Sensor:** `{payload['session']['sensor_source']}`",
        "",
        "## Feature changes",
        "",
        "| Feature | Before | After | Absolute change | Percent change |",
        "|---|---:|---:|---:|---:|",
    ]

    for item in payload.get("feature_deltas", []):
        percent = (
            f"{item['percent_change']:.2f}%"
            if item["percent_change"] is not None
            else "n/a"
        )
        lines.append(
            f"| {item['feature']} | {item['before']:.6f} | {item['after']:.6f} | "
            f"{item['absolute_change']:+.6f} | {percent} |"
        )

    lines.extend(["", "## Incidents", ""])
    incidents = payload.get("incidents", [])
    if not incidents:
        lines.append("- No incidents generated for this session.")
    else:
        for incident in incidents:
            lines.append(
                f"- **{incident['severity']}** risk={incident['risk_score']} — "
                f"{incident['title']}"
            )

    lines.extend(
        [
            "",
            "## Evidence",
            "",
        ]
    )
    bundle = payload.get("evidence_bundle")
    if bundle:
        for item in bundle.get("items", []):
            lines.append(
                f"- `{item['kind']}` — `{item['path']}` — sha256 `{item['sha256']}`"
            )
    else:
        lines.append("- No evidence files attached.")

    lines.extend(
        [
            "",
            "## Scope",
            "",
            "This report belongs to an explicitly authorized VantaWave lab target.",
            "The session is telemetry/analysis oriented; it does not imply authorization "
            "for third-party networks or arbitrary nearby devices.",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path
