from app.layers.diagnosis.diagnosis_schema import DiagnosisResult
from app.layers.routing.routing_schema import RoutingResult
from app.layers.retrieval.retrieval_schema import RetrievalResult
from app.layers.pedagogical_control.control_schema import PedagogicalDecision
from app.layers.pedagogical_control.hint_policy import (
    choose_hint_level,
    choose_strategy_type,
    should_allow_direct_answer,
    should_ask_question_first,
    choose_response_style,
    choose_cognitive_load,
    should_provide_affective_support,
    should_check_understanding,
    should_move_to_verification,
    select_chunk_ids,
    choose_teacher_goal,
)


class PedagogicalController:
    def __init__(self, use_llm_refinement: bool = False):
        self.use_llm_refinement = use_llm_refinement

    def decide(
        self,
        diagnosis: DiagnosisResult,
        routing: RoutingResult,
        retrieval: RetrievalResult,
        episode_state=None
    ) -> PedagogicalDecision:
        phase = "diagnose"
        if episode_state is not None:
            phase = getattr(episode_state, "phase", "diagnose")

        hint_level = choose_hint_level(
            diagnosis=diagnosis,
            routing=routing,
            retrieval=retrieval,
            episode_state=episode_state
        )

        strategy_type = choose_strategy_type(
            diagnosis=diagnosis,
            routing=routing,
            hint_level=hint_level,
            phase=phase
        )

        allow_direct_answer = should_allow_direct_answer(diagnosis, routing)
        ask_question_first = should_ask_question_first(
            diagnosis=diagnosis,
            routing=routing,
            retrieval=retrieval,
            hint_level=hint_level,
            phase=phase
        )
        response_style = choose_response_style(diagnosis, routing, hint_level, phase=phase)
        cognitive_load = choose_cognitive_load(diagnosis, hint_level)
        affective_support = should_provide_affective_support(diagnosis)
        check_understanding = should_check_understanding(diagnosis, routing, hint_level, phase=phase)
        chunk_ids = select_chunk_ids(retrieval)
        teacher_goal = choose_teacher_goal(diagnosis, routing, hint_level, phase=phase)

        # 将 6 类 strategy 映射到你当前系统里的 response strategy
        if strategy_type == "Closing":
            strategy = "closing"
        elif strategy_type == "Verification":
            strategy = "verification_check"
        elif strategy_type == "Conceptual":
            strategy = "conceptual_scaffold"
        elif strategy_type == "Diagnostic":
            strategy = "guided_hint"
        elif strategy_type == "Procedural":
            strategy = "stepwise_support"
        elif strategy_type == "Reflective":
            strategy = "guided_hint"
        elif strategy_type == "Hinting":
            strategy = "strong_hint_explanation"
        else:
            strategy = "guided_hint"

        notes = []
        if phase == "close":
            notes.append("CLOSE: stop teaching, give positive feedback, summarize, ask if student has other questions.")
        elif phase == "verify":
            notes.append("VERIFY: ask one confirmation question to check understanding.")
        elif hint_level == "L3":
            notes.append("L3: reduce questioning, provide structured steps.")
        elif hint_level == "L4":
            notes.append("L4: stop questioning, provide explanation, then verify/close.")

        if should_move_to_verification(hint_level, phase=phase):
            notes.append("After this turn, move to verification or close.")

        return PedagogicalDecision(
            strategy=strategy,
            hint_level=hint_level,
            allow_direct_answer=allow_direct_answer,
            ask_question_first=ask_question_first,
            use_retrieved_content=retrieval.total_hits > 0,
            response_style=response_style,
            cognitive_load=cognitive_load,
            affective_support=affective_support,
            should_check_understanding=check_understanding,
            selected_chunk_ids=chunk_ids,
            teacher_goal=teacher_goal,
            rationale=f"phase={phase}, strategy={strategy_type}, hint_level={hint_level}",
            notes=notes,
        )