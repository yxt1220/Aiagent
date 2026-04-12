from pathlib import Path
from typing import List, Dict

from app.core.config import GUIDE_FILE
from app.layers.retrieval.pdf_loader import load_structured_guide_chunks


def build_knowledge_base() -> List[Dict]:
    knowledge_base: List[Dict] = []
    guide_path = Path(GUIDE_FILE)

    if not guide_path.exists():
        print(f"[WARN] guide.pdf not found: {guide_path.resolve()}")
        return knowledge_base

    try:
        guide_chunks = load_structured_guide_chunks(str(guide_path), source_name="guide")
        knowledge_base.extend(guide_chunks)
        print(f"[INFO] Loaded {len(guide_chunks)} structured guide chunks")
    except Exception as e:
        print(f"[ERROR] Failed to load guide.pdf: {e}")

    print(f"[INFO] Total chunks in KNOWLEDGE_BASE: {len(knowledge_base)}")
    return knowledge_base


KNOWLEDGE_BASE = build_knowledge_base()