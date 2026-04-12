from typing import List
from app.layers.file_ingestion.ingestion_schema import UploadedChunk


def clean_text(text: str) -> str:
    return " ".join(text.split())


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1500,
    overlap: int = 200
) -> List[UploadedChunk]:
    text = clean_text(text)
    if not text:
        return []

    chunks: List[UploadedChunk] = []
    start = 0
    idx = 1
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                UploadedChunk(
                    chunk_id=f"chunk_{idx}",
                    content=chunk_text,
                    metadata={
                        "start": start,
                        "end": end,
                    },
                )
            )
            idx += 1

        if end == n:
            break

        start = max(0, end - overlap)

    return chunks