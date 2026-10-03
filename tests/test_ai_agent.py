import pytest

from vantawave.ai.analyst.agent import RestrictedAgentPlanner


def test_agent_plan_is_read_only_and_allowed():
    planner = RestrictedAgentPlanner()
    plan = planner.plan_incident_review()
    assert plan
    assert all(item.read_only for item in plan)
    assert all(planner.validate(item.action) for item in plan)


def test_agent_rejects_active_attack_action():
    planner = RestrictedAgentPlanner()
    with pytest.raises(PermissionError):
        planner.require_allowed("packet_injection")
