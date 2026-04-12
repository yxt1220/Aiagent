from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional


@dataclass
class PedagogicalDecision:
    strategy: str
    hint_level: str
    allow_direct_answer: bool
    ask_question_first: bool
    use_retrieved_content: bool
    response_style: str
    cognitive_load: str
    affective_support: bool
    should_check_understanding: bool
    selected_chunk_ids: List[str]
    teacher_goal: str
    rationale: str
    notes: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)