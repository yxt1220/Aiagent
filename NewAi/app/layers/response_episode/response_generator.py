import json

from app.layers.diagnosis.diagnosis_schema import DiagnosisResult
from app.layers.routing.routing_schema import RoutingResult
from app.layers.retrieval.retrieval_schema import RetrievalResult
from app.layers.pedagogical_control.control_schema import PedagogicalDecision
from app.layers.response_episode.response_prompt import RESPONSE_SYSTEM_PROMPT
from app.core.llm import call_llm


class ResponseGenerator:
    def __init__(self, use_llm_generation: bool = True):
        self.use_llm_generation = use_llm_generation

    def _get_selected_chunks(
        self,
        retrieval: RetrievalResult,
        selected_chunk_ids: list[str]
    ) -> list[dict]:
        selected = []
        selected_set = set(selected_chunk_ids)

        for chunk in retrieval.retrieved_chunks:
            if chunk.chunk_id in selected_set:
                selected.append({
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.source,
                    "content": chunk.content,
                    "metadata": chunk.metadata or {}
                })

        return selected

    def _build_prompt(
        self,
        user_input: str,
        diagnosis: DiagnosisResult,
        routing: RoutingResult,
        retrieval: RetrievalResult,
        pedagogy: PedagogicalDecision,
        context: str = ""
    ) -> str:
        selected_chunks = self._get_selected_chunks(
            retrieval=retrieval,
            selected_chunk_ids=pedagogy.selected_chunk_ids
        )[:2]

        # ── 如果有文件 context，拼进 prompt ──
        context_section = ""
        if context:
            context_section = f"""
Student's uploaded file context:
{context}
"""

        return f"""
Student latest message:
{user_input}
{context_section}
Diagnosis:
{json.dumps(diagnosis.to_dict(), ensure_ascii=False, indent=2)}

Routing:
{json.dumps(routing.to_dict(), ensure_ascii=False, indent=2)}

Pedagogical decision:
{json.dumps(pedagogy.to_dict(), ensure_ascii=False, indent=2)}

Retrieved guide evidence:
{json.dumps(selected_chunks, ensure_ascii=False, indent=2)}

Instruction:
Generate the next tutor response.
The reply should align with the pedagogical decision and use the guide evidence naturally.
If file context is provided above, reference the file the student is asking about. Files are listed most-recent-first; if the student says "this file" or refers to a specific filename, use that file's content. Do not mix up different files.
Do not dump the guide text verbatim.
Do not provide a final full answer.
""".strip()

    def _fallback_response(
        self,
        pedagogy: PedagogicalDecision
    ) -> str:
        if pedagogy.response_style == "closing":
            return "很好，你对这个概念的理解已经很到位了！你还有其他问题吗？或者我们可以换一个topic。"
        if pedagogy.response_style == "verification":
            return "你能用自己的话总结一下刚才讨论的关键点吗？"
        if pedagogy.hint_level == "L4":
            return "我先给你一个更直接的解释，再用一个小问题确认你是否已经抓住关键点。"
        if pedagogy.hint_level == "L3":
            return "我们先不继续追问，先把这件事拆成几个具体步骤来看。"
        if pedagogy.ask_question_first:
            return "你先说说，你现在更想确认方向，还是想把这个任务先拆成几个步骤？"
        return "我们先不急着确定最终答案，先把关键点缩小到一个可推进的下一步。"

    def generate(
        self,
        user_input: str,
        diagnosis: DiagnosisResult,
        routing: RoutingResult,
        retrieval: RetrievalResult,
        pedagogy: PedagogicalDecision,
        context: str = ""
    ) -> str:
        if not self.use_llm_generation:
            return self._fallback_response(pedagogy)

        prompt = self._build_prompt(
            user_input=user_input,
            diagnosis=diagnosis,
            routing=routing,
            retrieval=retrieval,
            pedagogy=pedagogy,
            context=context
        )

        raw = call_llm(RESPONSE_SYSTEM_PROMPT, prompt).strip()
        if not raw:
            return self._fallback_response(pedagogy)

        return raw