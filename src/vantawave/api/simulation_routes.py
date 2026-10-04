from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from vantawave.simulation.engine import run_simulation
from vantawave.simulation.reporting import save_simulation_report
from vantawave.simulation.scenarios import list_scenarios


router = APIRouter(prefix="/simulation", tags=["Adversary Simulation"])


class SimulationRequest(BaseModel):
    scenario_id: str
    intensity: int = Field(default=3, ge=1, le=5)
    duration_seconds: int = Field(default=60, ge=30, le=300)
    seed: int = 42
    persist_report: bool = True


@router.get("/capabilities")
def simulation_capabilities():
    return {
        "synthetic_only": True,
        "transmits_packets": False,
        "radio_interface_required": False,
        "real_credentials_tested": False,
        "active_attack_execution": False,
        "scenario_count": len(list_scenarios()),
        "pipeline": [
            "scenario",
            "synthetic events",
            "feature aggregation",
            "detector heuristics",
            "risk engine",
            "report",
        ],
    }


@router.get("/scenarios")
def scenarios():
    return {"scenarios": list_scenarios()}


@router.post("/run")
def run(payload: SimulationRequest):
    result = run_simulation(
        payload.scenario_id,
        intensity=payload.intensity,
        duration_seconds=payload.duration_seconds,
        seed=payload.seed,
    )
    body = result.to_dict()

    if payload.persist_report:
        json_path, md_path = save_simulation_report(
            body,
            "artifacts/simulation/reports",
        )
        body["report_paths"] = {
            "json": str(json_path),
            "markdown": str(md_path),
        }

    return body
