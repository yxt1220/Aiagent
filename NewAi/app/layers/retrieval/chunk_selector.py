from typing import List, Optional

from app.layers.retrieval.knowledge_base import KNOWLEDGE_BASE
from app.layers.retrieval.retrieval_schema import RetrievedChunk


def simple_score(query: str, chunk: dict) -> float:
    query_lower = query.lower()
    content = chunk.get("content", "").lower()
    score = 0.0

    for token in query_lower.split():
        if token in content:
            score += 0.2

    metadata = chunk.get("metadata", {})
    chapter_title = (metadata.get("chapter_title") or "").lower()
    section_type = (metadata.get("section_type") or "").lower()

    for token in query_lower.split():
        if token in chapter_title:
            score += 0.5
        if token in section_type:
            score += 0.3

    if chunk.get("source") == "guide":
        score += 0.1

    return score


def select_top_chunks(
    query: str,
    top_k: int = 3,
    chapter_number: Optional[int] = None,
    allowed_section_types: Optional[List[str]] = None,
) -> List[RetrievedChunk]:
    scored = []
    allowed_lower = set(s.lower() for s in allowed_section_types) if allowed_section_types else None

    for chunk in KNOWLEDGE_BASE:
        metadata = chunk.get("metadata", {})
        chunk_chapter = metadata.get("chapter_number")
        chunk_section = (metadata.get("section_type") or "").lower()

        if chapter_number is not None and chunk_chapter != chapter_number:
            continue

        if allowed_lower is not None and chunk_section not in allowed_lower:
            continue

        score = simple_score(query, chunk)
        if score > 0:
            scored.append(
                RetrievedChunk(
                    chunk_id=chunk["chunk_id"],
                    source=chunk["source"],
                    content=chunk["content"],
                    score=round(score, 3),
                    metadata=metadata
                )
            )

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]