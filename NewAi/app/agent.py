from app.layers.diagnosis.diagnosis_engine import DiagnosisEngine
from app.layers.routing.router import Router
from app.layers.retrieval.retriever import Retriever
from app.layers.pedagogical_control.controller import PedagogicalController
from app.layers.response_episode.response_generator import ResponseGenerator
from app.layers.response_episode.episode_manager import EpisodeManager

from app.core.config import (
    RETRIEVAL_TOP_K,
    USE_LLM_ROUTING_FALLBACK,
    USE_LLM_PEDAGOGICAL_REFINEMENT,
    USE_LLM_RESPONSE_GENERATION,
    USE_LLM_CONCEPT_EXTRACTION,
)


class TutorAgent:
    def __init__(self):
        self.diagnosis_engine = DiagnosisEngine(
            use_llm_concept_extraction=USE_LLM_CONCEPT_EXTRACTION
        )
        self.router = Router(use_llm_fallback=USE_LLM_ROUTING_FALLBACK)
        self.retriever = Retriever(top_k=RETRIEVAL_TOP_K)
        self.controller = PedagogicalController(
            use_llm_refinement=USE_LLM_PEDAGOGICAL_REFINEMENT
        )
        self.response_generator = ResponseGenerator(
            use_llm_generation=USE_LLM_RESPONSE_GENERATION
        )
        self.episode_manager = EpisodeManager()

    def _build_recent_turns(self, max_turns: int = 3):
        episode_state = self.episode_manager.get_state()
        recent_turns = []

        for turn in episode_state.recent_turns[-max_turns:]:
            recent_turns.append({"role": "user", "content": turn.user_input})
            recent_turns.append({"role": "assistant", "content": turn.assistant_response})

        return recent_turns

    def run(self, user_input: str, context: str = ""):
        try:
            episode_state = self.episode_manager.get_state()
            recent_turns = self._build_recent_turns(max_turns=3)

            diagnosis_result = self.diagnosis_engine.run(
                user_input=user_input,
                context=context,
                recent_turns=recent_turns,
                episode_state=episode_state.to_dict(),
            )

            routing_result = self.router.route(diagnosis_result, context)

            retrieval_result = self.retriever.retrieve(
                user_input=user_input,
                diagnosis=diagnosis_result,
                routing=routing_result,
            )

            pedagogical_result = self.controller.decide(
                diagnosis=diagnosis_result,
                routing=routing_result,
                retrieval=retrieval_result,
                episode_state=episode_state,
            )

            response = self.response_generator.generate(
                user_input=user_input,
                diagnosis=diagnosis_result,
                routing=routing_result,
                retrieval=retrieval_result,
                pedagogy=pedagogical_result,
                context=context,
            )

            updated_episode_state = self.episode_manager.update(
                user_input=user_input,
                diagnosis=diagnosis_result,
                routing=routing_result,
                pedagogy=pedagogical_result,
                assistant_response=response,
            )

            return {
                "response": response,
                "diagnosis": diagnosis_result.to_dict(),
                "routing": routing_result.to_dict(),
                "retrieval": retrieval_result.to_dict(),
                "pedagogical_control": pedagogical_result.to_dict(),
                "episode_state": updated_episode_state.to_dict(),
            }

        except Exception as e:
            return {
                "response": f"系统运行出错：{str(e)}",
                "diagnosis": None,
                "routing": None,
                "retrieval": None,
                "pedagogical_control": None,
                "episode_state": None,
            }

    def chat(self, user_input: str, context: str = "") -> str:
        return self.run(user_input, context)["response"]

    def reset_episode(self, episode_id: str = "ep_001"):
        self.episode_manager.reset(episode_id=episode_id)