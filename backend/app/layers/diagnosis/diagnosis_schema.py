from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List


@dataclass
class DiagnosisResult:
    problem_type: str
    student_state: str
    intent: str
    needs_clarification: bool
    is_off_topic: bool
    is_nonsense: bool
    asks_for_direct_answer: bool
    confidence: float
    rationale: str
    detected_concepts: Optional[List[str]] = None
    context_relation: str = "unknown"
    is_follow_up: bool = False
    answers_previous_question: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def fallback(cls, reason: str = "Fallback diagnosis used."):
        return cls(
            problem_type="unknown",
            student_state="unknown",
            intent="unknown",
            needs_clarification=False,
            is_off_topic=False,
            is_nonsense=False,
            asks_for_direct_answer=False,
            confidence=0.0,
            rationale=reason,
            detected_concepts=[],
            context_relation="unknown",
            is_follow_up=False,
            answers_previous_question=False,
        )