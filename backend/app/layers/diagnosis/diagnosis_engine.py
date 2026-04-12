import json
from typing import Optional, List, Dict, Any

from app.core.llm import call_llm
from app.layers.diagnosis.diagnosis_prompt import DIAGNOSIS_SYSTEM_PROMPT
from app.layers.diagnosis.diagnosis_schema import DiagnosisResult
from app.layers.diagnosis.diagnosis_utils import (
    looks_empty,
    extract_simple_concepts,
    extract_json_object,
)


class DiagnosisEngine:
    def __init__(self, use_llm_concept_extraction: bool = True):
        self.use_llm_concept_extraction = use_llm_concept_extraction

    def _minimal_precheck(self, user_input: str) -> Optional[DiagnosisResult]:
        if looks_empty(user_input):
            return DiagnosisResult(
                problem_type="unknown",
                student_state="unknown",
                intent="unknown",
                needs_clarification=True,
                is_off_topic=False,
                is_nonsense=True,
                asks_for_direct_answer=False,
                confidence=1.0,
                rationale="Empty input.",
                detected_concepts=[],
                context_relation="unknown",
                is_follow_up=False,
                answers_previous_question=False,
            )
        return None

    def _build_user_prompt(
        self,
        user_input: str,
        context: str = "",
        recent_turns: Optional[List[Dict[str, str]]] = None,
        episode_state: Optional[Dict[str, Any]] = None,
    ) -> str:
        turns_text = json.dumps(recent_turns or [], ensure_ascii=False, indent=2)
        episode_text = json.dumps(episode_state or {}, ensure_ascii=False, indent=2)

        return f"""
Student latest message:
{user_input}

Conversation summary:
{context}

Recent turns:
{turns_text}

Episode state:
{episode_text}
""".strip()

    def _parse_llm_output(self, raw_output: str) -> DiagnosisResult:
        data = extract_json_object(raw_output)
        if data is None:
            return DiagnosisResult.fallback(
                reason=f"Diagnosis parse failed. Raw output: {raw_output[:300]}"
            )

        try:
            detected_concepts = data.get("detected_concepts", [])
            if not isinstance(detected_concepts, list):
                detected_concepts = []

            cleaned_concepts = []
            for item in detected_concepts:
                if isinstance(item, str):
                    item = item.strip().lower()
                    if item:
                        cleaned_concepts.append(item)

            return DiagnosisResult(
                problem_type=data.get("problem_type", "unknown"),
                student_state=data.get("student_state", "unknown"),
                intent=data.get("intent", "unknown"),
                needs_clarification=bool(data.get("needs_clarification", False)),
                is_off_topic=bool(data.get("is_off_topic", False)),
                is_nonsense=bool(data.get("is_nonsense", False)),
                asks_for_direct_answer=bool(data.get("asks_for_direct_answer", False)),
                confidence=float(data.get("confidence", 0.0)),
                rationale=data.get("rationale", "No rationale provided."),
                detected_concepts=cleaned_concepts,
                context_relation=data.get("context_relation", "unknown"),
                is_follow_up=bool(data.get("is_follow_up", False)),
                answers_previous_question=bool(data.get("answers_previous_question", False)),
            )
        except Exception as e:
            return DiagnosisResult.fallback(
                reason=f"Diagnosis parse failed after JSON extraction: {str(e)}"
            )

    def _post_process(self, user_input: str, result: DiagnosisResult) -> DiagnosisResult:
        concepts = extract_simple_concepts(
            user_input,
            use_llm=self.use_llm_concept_extraction
        )
        if not result.detected_concepts:
            result.detected_concepts = concepts
        result.confidence = max(0.0, min(1.0, float(result.confidence)))
        return result

    def run(
        self,
        user_input: str,
        context: str = "",
        recent_turns: Optional[List[Dict[str, str]]] = None,
        episode_state: Optional[Dict[str, Any]] = None,
    ) -> DiagnosisResult:
        precheck = self._minimal_precheck(user_input)
        if precheck is not None:
            return precheck

        prompt = self._build_user_prompt(
            user_input=user_input,
            context=context,
            recent_turns=recent_turns,
            episode_state=episode_state,
        )
        raw_output = call_llm(DIAGNOSIS_SYSTEM_PROMPT, prompt)
        print("\n[DEBUG] diagnosis raw_output:")
        print(raw_output)

        result = self._parse_llm_output(raw_output)
        return self._post_process(user_input, result)