from app.layers.diagnosis.diagnosis_schema import DiagnosisResult
from app.layers.routing.routing_schema import RoutingResult
from app.layers.retrieval.retrieval_schema import RetrievalResult
from app.layers.retrieval.chunk_selector import select_top_chunks
from app.layers.routing.trigger_matrix import infer_chapter_from_text


class Retriever:
    def __init__(self, use_query_rewrite: bool = False, top_k: int = 3):
        self.use_query_rewrite = use_query_rewrite
        self.top_k = top_k

    def _build_query(
        self,
        user_input: str,
        diagnosis: DiagnosisResult,
        routing: RoutingResult
    ) -> str:
        concept_part = " ".join(diagnosis.detected_concepts or [])
        return f"{user_input} {concept_part}".strip()

    def retrieve(
        self,
        user_input: str,
        diagnosis: DiagnosisResult,
        routing: RoutingResult
    ) -> RetrievalResult:
        if not routing.need_retrieval:
            return RetrievalResult.empty(
                query_used="",
                retrieval_mode=routing.retrieval_mode or "none"
            )

        query = self._build_query(user_input, diagnosis, routing)

        target_chapter = routing.target_chapter
        target_section_types = routing.target_section_types

        if target_chapter is None:
            inferred = infer_chapter_from_text(query)
            if inferred:
                target_chapter = inferred["chapter_number"]
                if not target_section_types:
                    target_section_types = inferred["section_types"]

        chunks = select_top_chunks(
            query=query,
            top_k=self.top_k,
            chapter_number=target_chapter,
            allowed_section_types=target_section_types,
        )

        if not chunks:
            return RetrievalResult(
                query_used=query,
                retrieval_mode=routing.retrieval_mode or "light",
                retrieved_chunks=[],
                total_hits=0,
                confidence=0.1,
                retrieval_notes=[
                    "No chunk matched the targeted guide retrieval.",
                    f"target_chapter={target_chapter}",
                    f"target_section_types={target_section_types}",
                ],
            )

        avg_score = sum(chunk.score for chunk in chunks) / len(chunks)
        confidence = min(1.0, round(avg_score / 3.0, 3))

        return RetrievalResult(
            query_used=query,
            retrieval_mode=routing.retrieval_mode or "light",
            retrieved_chunks=chunks,
            total_hits=len(chunks),
            confidence=confidence,
            retrieval_notes=[
                f"Retrieved {len(chunks)} chunk(s).",
                f"target_chapter={target_chapter}",
                f"target_section_types={target_section_types}",
            ],
        )