from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List


@dataclass
class RoutingResult:
    route: str
    reason: str
    need_retrieval: bool
    retrieval_mode: Optional[str]
    response_mode: str
    escalate_to_pedagogy: bool
    terminate_episode: bool
    priority: str
    recommended_next_step: str
    notes: Optional[List[str]] = None
    target_chapter: Optional[int] = None
    target_section_types: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def fallback(cls, reason: str = "Fallback routing used."):
        return cls(
            route="clarify",
            reason=reason,
            need_retrieval=False,
            retrieval_mode=None,
            response_mode="ask_clarification",
            escalate_to_pedagogy=False,
            terminate_episode=False,
            priority="medium",
            recommended_next_step="ask student to clarify",
            notes=[],
            target_chapter=None,
            target_section_types=None,
        )