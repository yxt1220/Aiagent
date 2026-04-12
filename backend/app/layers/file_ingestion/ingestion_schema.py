from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional


@dataclass
class UploadedChunk:
    chunk_id: str
    content: str
    metadata: Optional[dict] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedFile:
    file_id: str
    file_name: str
    file_type: str
    raw_text: str
    chunks: List[UploadedChunk]
    structured_summary: Optional[dict] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "raw_text": self.raw_text,
            "chunks": [c.to_dict() for c in self.chunks],
            "structured_summary": self.structured_summary,
        }