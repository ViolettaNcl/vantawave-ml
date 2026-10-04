from __future__ import annotations

from pathlib import Path
import json


def save_simulation_report(result: dict, output_dir: str | Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    simulation_id = result["simulation_id"]
    json_path = output_dir / f"{simulation_id}.json"
    md_path = output_dir / f"{simulation_id}.md"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    scenario = result["scenario"]
    risk = result["risk"]

    lines = [
        "# VantaWave Adversary Simulation Report",
        "",
        f"**Simulation:** `{simulation_id}`",
        f"**Scenario:** {scenario['title']}",
        f"**Category:** {scenario['category']}",
        f"**Intensity:** {result['intensity']}/5",
        f"**Risk:** {risk['severity']} ({risk['score']}/100)",
        "",
        "> This report was generated from synthetic/adversary-simulation events. "
        "No packets were transmitted.",
        "",
        "## Detections",
        "",
    ]
    detections = result.get("detections", [])
    lines.extend([f"- {item}" for item in detections] or ["- No detector rule triggered."])

    lines.extend(
        [
            "",
            "## Feature deltas",
            "",
            "| Feature | Baseline | Scenario | Δ |",
            "|---|---:|---:|---:|",
        ]
    )
    for item in result.get("feature_deltas", []):
        lines.append(
            f"| {item['feature']} | {item['before']:.4f} | "
            f"{item['after']:.4f} | {item['absolute_change']:+.4f} |"
        )

    lines.extend(
        [
            "",
            "## Learning goal",
            "",
            scenario["learning_goal"],
            "",
            "## Safety boundary",
            "",
            scenario["safe_boundary"],
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path
