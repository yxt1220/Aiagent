from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class RetrievedChunk:
    chunk_id: str
    source: str
    content: str
    score: float
    metadata: Optional[dict] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class RetrievalResult:
    query_used: str
    retrieval_mode: str
    retrieved_chunks: List[RetrievedChunk]
    total_hits: int
    confidence: float
    retrieval_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_used": self.query_used,
            "retrieval_mode": self.retrieval_mode,
            "retrieved_chunks": [chunk.to_dict() for chunk in self.retrieved_chunks],
            "total_hits": self.total_hits,
            "confidence": self.confidence,
            "retrieval_notes": self.retrieval_notes,
        }

    @classmethod
    def empty(cls, query_used: str = "", retrieval_mode: str = "light"):
        return cls(
            query_used=query_used,
            retrieval_mode=retrieval_mode,
            retrieved_chunks=[],
            total_hits=0,
            confidence=0.0,
            retrieval_notes=["No relevant content retrieved."],
        )