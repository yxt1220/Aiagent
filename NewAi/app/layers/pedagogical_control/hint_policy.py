from typing import List, Optional

from app.layers.diagnosis.diagnosis_schema import DiagnosisResult
from app.layers.routing.routing_schema import RoutingResult
from app.layers.retrieval.retrieval_schema import RetrievalResult


def choose_hint_level(
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    retrieval: RetrievalResult,
    episode_state=None
) -> str:
    """
    L1: 轻微引导（socratic）
    L2: 方向提示
    L3: 具体步骤
    L4: 接近答案 / 解释性提示
    """

    turn_count = 0
    failed_attempts = 0
    phase = "diagnose"

    if episode_state is not None:
        turn_count = getattr(episode_state, "turn_count", 0)
        failed_attempts = getattr(episode_state, "guided_hint_count", 0)
        phase = getattr(episode_state, "phase", "diagnose")

    # ── Close 阶段：不再升级，保持最低干预 ──
    if phase == "close":
        return "L1"

    # ── Verify 阶段：轻量确认，不再教新东西 ──
    if phase == "verify":
        return "L1"

    # ── 首轮强制 L1 ──
    if turn_count == 0:
        return "L1"

    # ── frustrated → L3 ──
    if diagnosis.student_state in ["frustrated"]:
        return "L3"

    # ── stuck → L3 ──
    if diagnosis.student_state in ["stuck"]:
        return "L3"

    # ── 多次 L3/L4 仍失败 → L4 ──
    if failed_attempts >= 2:
        return "L4"

    # ── verify_answer → L2 ──
    if diagnosis.intent == "verify_answer":
        return "L2"

    # ── step_guidance → L2 ──
    if routing.response_mode == "step_guidance":
        return "L2"

    # ── scaffolded_explanation → L2 ──
    if routing.response_mode == "scaffolded_explanation":
        return "L2"

    return "L1"


def choose_strategy_type(
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    hint_level: str,
    phase: str = "scaffold"
) -> str:
    """
    文档中的 6 类 strategy + Verification + Closing
    """
    if phase == "close":
        return "Closing"

    if phase == "verify":
        return "Verification"

    if diagnosis.intent == "verify_answer":
        return "Reflective" if hint_level in ["L1", "L2"] else "Procedural"

    if diagnosis.student_state in ["stuck"] and hint_level == "L3":
        return "Procedural"

    if diagnosis.student_state in ["frustrated"] or hint_level == "L4":
        return "Hinting"

    if routing.response_mode == "step_guidance":
        return "Procedural"

    if routing.response_mode == "scaffolded_explanation":
        return "Conceptual"

    if routing.response_mode == "meta_guidance":
        return "Reflective"

    return "Diagnostic"


def should_allow_direct_answer(
    diagnosis: DiagnosisResult,
    routing: RoutingResult
) -> bool:
    return False


def should_ask_question_first(
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    retrieval: RetrievalResult,
    hint_level: str,
    phase: str = "scaffold"
) -> bool:
    """
    Close: 不问
    Verify: 问一个确认性问题
    L1: 问
    L2: 问 + 轻提示
    L3: 少问，多讲
    L4: 不问
    """
    if phase == "close":
        return False

    if phase == "verify":
        return True

    if hint_level == "L4":
        return False

    if hint_level == "L3":
        return False

    return True


def choose_response_style(
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    hint_level: str,
    phase: str = "scaffold"
) -> str:
    if phase == "close":
        return "closing"
    if phase == "verify":
        return "verification"
    if hint_level == "L4":
        return "direct_explanatory"
    if hint_level == "L3":
        return "structured_procedural"
    if hint_level == "L2":
        return "guided"
    return "socratic"


def choose_cognitive_load(
    diagnosis: DiagnosisResult,
    hint_level: str
) -> str:
    if hint_level == "L4":
        return "low"
    if hint_level == "L3":
        return "medium"
    return "medium"


def should_provide_affective_support(diagnosis: DiagnosisResult) -> bool:
    return diagnosis.student_state in ["frustrated", "stuck"]


def should_check_understanding(
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    hint_level: str,
    phase: str = "scaffold"
) -> bool:
    if phase in ["verify", "close"]:
        return True
    if hint_level == "L4":
        return True
    return routing.response_mode in ["step_guidance", "scaffolded_explanation", "controlled_scaffold"]


def should_move_to_verification(hint_level: str, phase: str = "scaffold") -> bool:
    return phase in ["verify", "close"] or hint_level == "L4"


def select_chunk_ids(retrieval: RetrievalResult, max_chunks: int = 2) -> List[str]:
    return [chunk.chunk_id for chunk in retrieval.retrieved_chunks[:max_chunks]]


def choose_teacher_goal(
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    hint_level: str,
    phase: str = "scaffold"
) -> str:
    if phase == "close":
        return "provide brief positive feedback, summarize, and ask if the student has other questions"
    if phase == "verify":
        return "confirm student's understanding with a simple check question"
    if hint_level == "L4":
        return "give a strong conceptual explanation and then verify understanding"
    if hint_level == "L3":
        return "give structured procedural guidance so the student can act"
    if routing.target_chapter == 4:
        return "help the student narrow and compare candidate methods"
    if routing.target_chapter == 3:
        return "help the student reason through preprocessing decisions"
    if routing.target_chapter == 6:
        return "help the student interpret evaluation meaningfully"
    return "support the student's next learning step"
