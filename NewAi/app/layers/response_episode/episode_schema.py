from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional


@dataclass
class EpisodeTurn:
    user_input: str
    diagnosis_summary: str
    routing_summary: str
    pedagogical_summary: str
    assistant_response: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EpisodeState:
    episode_id: str
    turn_count: int
    current_goal: str
    current_hint_level: str
    resolved: bool
    needs_escalation: bool
    clarification_count: int = 0
    guided_hint_count: int = 0
    phase: str = "diagnose"  # diagnose → scaffold → verify → close
    mastery_signals: int = 0  # 学生展示理解的次数
    consecutive_no_progress: int = 0  # 连续无进展轮数
    max_turns: int = 6  # 硬限制
    recent_turns: List[EpisodeTurn] = field(default_factory=list)
    last_student_state: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "turn_count": self.turn_count,
            "current_goal": self.current_goal,
            "current_hint_level": self.current_hint_level,
            "resolved": self.resolved,
            "needs_escalation": self.needs_escalation,
            "clarification_count": self.clarification_count,
            "guided_hint_count": self.guided_hint_count,
            "phase": self.phase,
            "mastery_signals": self.mastery_signals,
            "consecutive_no_progress": self.consecutive_no_progress,
            "max_turns": self.max_turns,
            "recent_turns": [t.to_dict() for t in self.recent_turns],
            "last_student_state": self.last_student_state,
            "notes": self.notes,
        }

    @classmethod
    def new_episode(cls, episode_id: str = "ep_001"):
        return cls(
            episode_id=episode_id,
            turn_count=0,
            current_goal="support the student's learning",
            current_hint_level="L1",
            resolved=False,
            needs_escalation=False,
        )