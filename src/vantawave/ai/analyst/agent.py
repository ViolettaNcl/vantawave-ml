from __future__ import annotations

from dataclasses import asdict, dataclass


ALLOWED_ACTIONS = {
    "summarize_incident",
    "retrieve_project_knowledge",
    "compare_historical_incidents",
    "suggest_defensive_checks",
    "generate_report",
    "refresh_read_only_monitoring_context",
}

FORBIDDEN_ACTIONS = {
    "packet_injection",
    "deauthentication_attack",
    "credential_capture",
    "credential_theft",
    "third_party_targeting",
    "brute_force",
    "exploit_execution",
}


@dataclass(frozen=True)
class AgentAction:
    action: str
    reason: str
    read_only: bool = True

    def to_dict(self):
        return asdict(self)


class RestrictedAgentPlanner:
    def validate(self, action: str) -> bool:
        return action in ALLOWED_ACTIONS

    def plan_incident_review(self, *, include_history: bool = True) -> list[AgentAction]:
        plan = [
            AgentAction(
                action="summarize_incident",
                reason="Establish the persisted incident facts.",
            ),
            AgentAction(
                action="retrieve_project_knowledge",
                reason="Retrieve defensive documentation relevant to the incident.",
            ),
        ]
        if include_history:
            plan.append(
                AgentAction(
                    action="compare_historical_incidents",
                    reason="Compare only against persisted incident history.",
                )
            )
        plan.extend(
            [
                AgentAction(
                    action="suggest_defensive_checks",
                    reason="Offer non-destructive verification steps.",
                ),
                AgentAction(
                    action="generate_report",
                    reason="Produce an evidence-grounded final report.",
                ),
            ]
        )
        return plan

    def require_allowed(self, action: str):
        if action in FORBIDDEN_ACTIONS or action not in ALLOWED_ACTIONS:
            raise PermissionError(f"Agent action '{action}' is not permitted.")
