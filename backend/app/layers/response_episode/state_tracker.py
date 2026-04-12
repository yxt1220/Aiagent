from app.layers.response_episode.episode_schema import EpisodeState, EpisodeTurn
from app.layers.diagnosis.diagnosis_schema import DiagnosisResult
from app.layers.routing.routing_schema import RoutingResult
from app.layers.pedagogical_control.control_schema import PedagogicalDecision


def summarize_diagnosis(diagnosis: DiagnosisResult) -> str:
    return f"{diagnosis.problem_type}/{diagnosis.student_state}/{diagnosis.intent}"


def summarize_routing(routing: RoutingResult) -> str:
    return f"{routing.route}/{routing.response_mode}/ch{routing.target_chapter}"


def summarize_pedagogy(pedagogy: PedagogicalDecision) -> str:
    return f"{pedagogy.strategy}/{pedagogy.hint_level}"


# ── Mastery Detection ──
# 只有 clear 才算真正掌握
MASTERY_STATES = {"clear"}
MASTERY_INTENTS = {"answer_tutor_question"}
NO_PROGRESS_STATES = {"stuck", "frustrated", "confused", "unknown"}

# 关键词硬检测
NO_PROGRESS_KEYWORDS = [
    "不知道", "no idea", "i don't know", "idk", "no clue",
    "不会", "不了解", "不清楚", "不太懂", "不明白",
    "没思路", "不确定", "不懂", "help me", "告诉我答案",
    "give me the answer", "just tell me",
]


def detect_mastery_signal(diagnosis: DiagnosisResult) -> bool:
    """只有 clear 才算掌握"""
    if diagnosis.student_state in MASTERY_STATES:
        return True
    if diagnosis.intent in MASTERY_INTENTS and diagnosis.student_state not in NO_PROGRESS_STATES:
        return True
    return False


def detect_no_progress(diagnosis: DiagnosisResult, user_input: str = "") -> bool:
    """LLM 判断 or 关键词硬匹配"""
    if diagnosis.student_state in NO_PROGRESS_STATES:
        return True
    lowered = user_input.strip().lower()
    for kw in NO_PROGRESS_KEYWORDS:
        if kw in lowered:
            return True
    return False


# ── Phase Transition Logic ──
def compute_next_phase(
    episode_state: EpisodeState,
    diagnosis: DiagnosisResult,
    pedagogy: PedagogicalDecision,
) -> str:
    current_phase = episode_state.phase
    turn_count = episode_state.turn_count  # 已经 +1 了
    mastery_signals = episode_state.mastery_signals
    consecutive_no_progress = episode_state.consecutive_no_progress
    max_turns = episode_state.max_turns

    # ── 已经 close 了就不再变 ──
    if current_phase == "close":
        return "close"

    # ── 硬限制：超过 max_turns 强制 close ──
    if turn_count >= max_turns:
        return "close"

    # ── 前 3 轮不允许 verify/close（防止 LLM 过早判 mastery） ──
    if turn_count < 3:
        if current_phase == "diagnose" and turn_count >= 1:
            return "scaffold"
        return current_phase

    # ── mastery: 3 次展示理解 → 直接 close ──
    if mastery_signals >= 3:
        return "close"

    # ── mastery: 2 次展示理解 → verify ──
    if mastery_signals >= 2:
        return "verify"

    # ── 连续 4 次无进展 → close（走完了 L1→L3→L4 还不会） ──
    if consecutive_no_progress >= 4:
        return "close"

    # ── 首轮结束后从 diagnose → scaffold ──
    if current_phase == "diagnose" and turn_count >= 1:
        return "scaffold"

    return current_phase


def update_episode_state(
    episode_state: EpisodeState,
    user_input: str,
    diagnosis: DiagnosisResult,
    routing: RoutingResult,
    pedagogy: PedagogicalDecision,
    assistant_response: str
) -> EpisodeState:
    episode_state.turn_count += 1
    episode_state.current_goal = pedagogy.teacher_goal
    episode_state.current_hint_level = pedagogy.hint_level
    episode_state.last_student_state = diagnosis.student_state

    if routing.route == "clarify":
        episode_state.clarification_count += 1

    # ── 追踪高 hint 次数 ──
    if pedagogy.hint_level in ("L3", "L4"):
        episode_state.guided_hint_count += 1

    # ── L4 后标记 ──
    if pedagogy.hint_level == "L4":
        if not any("post_L4" in n for n in episode_state.notes):
            episode_state.notes.append("post_L4: next turn should verify or close")

    # ── Mastery detection ──
    if detect_mastery_signal(diagnosis):
        episode_state.mastery_signals += 1
        episode_state.consecutive_no_progress = 0
    elif detect_no_progress(diagnosis, user_input=user_input):
        episode_state.consecutive_no_progress += 1
    else:
        pass

    # ── 连续 2 次无进展 → 强制标记 stuck，让 hint 升到 L3 ──
    if episode_state.consecutive_no_progress >= 2 and episode_state.last_student_state != "stuck":
        episode_state.last_student_state = "stuck"

    # ── Phase transition ──
    episode_state.phase = compute_next_phase(episode_state, diagnosis, pedagogy)

    # ── close 阶段标记 resolved ──
    if episode_state.phase == "close":
        episode_state.resolved = True

    turn = EpisodeTurn(
        user_input=user_input,
        diagnosis_summary=summarize_diagnosis(diagnosis),
        routing_summary=summarize_routing(routing),
        pedagogical_summary=summarize_pedagogy(pedagogy),
        assistant_response=assistant_response,
    )
    episode_state.recent_turns.append(turn)

    if len(episode_state.recent_turns) > 5:
        episode_state.recent_turns = episode_state.recent_turns[-5:]

    if routing.terminate_episode:
        episode_state.resolved = True

    return episode_state
