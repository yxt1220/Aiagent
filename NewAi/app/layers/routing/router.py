import json

from app.layers.routing.routing_schema import RoutingResult
from app.layers.routing.routing_rules import apply_routing_rules
from app.layers.diagnosis.diagnosis_schema import DiagnosisResult


class Router:
    def __init__(self, use_llm_fallback: bool = False):
        self.use_llm_fallback = use_llm_fallback

    def route(self, diagnosis: DiagnosisResult, context: str = "") -> RoutingResult:
        rule_result = apply_routing_rules(diagnosis)

        if rule_result is not None:
            return RoutingResult(
                route=rule_result["route"],
                reason=rule_result["reason"],
                need_retrieval=rule_result["need_retrieval"],
                retrieval_mode=rule_result["retrieval_mode"],
                response_mode=rule_result["response_mode"],
                escalate_to_pedagogy=rule_result["escalate_to_pedagogy"],
                terminate_episode=rule_result["terminate_episode"],
                priority=rule_result["priority"],
                recommended_next_step=rule_result["recommended_next_step"],
                notes=rule_result.get("notes", []),
                target_chapter=rule_result.get("target_chapter"),
                target_section_types=rule_result.get("target_section_types"),
            )

        return RoutingResult(
            route="retrieve_then_scaffold",
            reason="Default fallback for a valid learning request.",
            need_retrieval=True,
            retrieval_mode="light",
            response_mode="scaffolded_explanation",
            escalate_to_pedagogy=True,
            terminate_episode=False,
            priority="medium",
            recommended_next_step="retrieve light support and continue with pedagogical control",
            notes=["Fallback route."],
            target_chapter=None,
            target_section_types=None,
        )