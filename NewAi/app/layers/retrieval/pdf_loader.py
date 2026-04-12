from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

from pypdf import PdfReader


SECTION_HEADERS = [
    "Objective",
    "Expected Outputs",
    "Common Obstacles",
    "Guiding Questions",
    "Typical Mistakes",
    "Cognitive Misconceptions",
    "Tips for Scaffolding Chatbot",
    "Socratic Question Prompts",
    "Examples of Methods by Task",
    "Tips for RAG Chatbot",
]

CHAPTER_PATTERN = re.compile(
    r"(Chapter\s+(\d+)\s*[:–-]\s*(.+))",
    flags=re.IGNORECASE
)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_long_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    text = clean_text(text)
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def detect_chapter(text: str) -> Optional[Dict]:
    match = CHAPTER_PATTERN.search(text)
    if not match:
        return None

    return {
        "chapter_number": int(match.group(2)),
        "chapter_title": match.group(3).strip()
    }


def find_section_boundaries(lines: List[str]) -> List[Tuple[int, str]]:
    boundaries = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        for header in SECTION_HEADERS:
            if stripped == header:
                boundaries.append((i, header))
                break
    return boundaries


def split_page_by_sections(page_text: str) -> List[Dict]:
    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    if not lines:
        return []

    chapter_info = detect_chapter(page_text)
    boundaries = find_section_boundaries(lines)

    if not boundaries:
        return [{
            "chapter_number": chapter_info["chapter_number"] if chapter_info else None,
            "chapter_title": chapter_info["chapter_title"] if chapter_info else None,
            "section_type": "raw_page",
            "content": clean_text("\n".join(lines))
        }]

    sections = []
    for idx, (start_i, header) in enumerate(boundaries):
        end_i = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        content_lines = lines[start_i + 1:end_i]
        content = clean_text("\n".join(content_lines))

        sections.append({
            "chapter_number": chapter_info["chapter_number"] if chapter_info else None,
            "chapter_title": chapter_info["chapter_title"] if chapter_info else None,
            "section_type": header,
            "content": content
        })

    return sections


def load_structured_guide_chunks(pdf_path: str, source_name: str = "guide") -> List[Dict]:
    pdf_file = Path(pdf_path)
    reader = PdfReader(str(pdf_file))
    all_chunks: List[Dict] = []

    current_chapter_number = None
    current_chapter_title = None

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        page_text = clean_text(page.extract_text() or "")
        if not page_text:
            continue

        detected = detect_chapter(page_text)
        if detected:
            current_chapter_number = detected["chapter_number"]
            current_chapter_title = detected["chapter_title"]

        section_blocks = split_page_by_sections(page_text)

        for block_idx, block in enumerate(section_blocks, start=1):
            chapter_number = block["chapter_number"] or current_chapter_number
            chapter_title = block["chapter_title"] or current_chapter_title
            section_type = block["section_type"]
            content = block["content"]

            if not content:
                continue

            subchunks = split_long_text(content, chunk_size=1200, overlap=150)
            for sub_idx, subchunk in enumerate(subchunks, start=1):
                chunk_id = (
                    f"{source_name}_ch{chapter_number or 'x'}"
                    f"_p{page_num}_s{block_idx}_c{sub_idx}"
                )

                all_chunks.append({
                    "chunk_id": chunk_id,
                    "source": source_name,
                    "content": subchunk,
                    "keywords": [],
                    "metadata": {
                        "pdf_path": str(pdf_file),
                        "page": page_num,
                        "chapter_number": chapter_number,
                        "chapter_title": chapter_title,
                        "section_type": section_type,
                        "chunk_index": sub_idx,
                    }
                })

    return all_chunks