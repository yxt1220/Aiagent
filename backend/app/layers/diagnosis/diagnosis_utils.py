import json
import re
from typing import List, Optional

from app.core.llm import call_llm


NONSENSE_PATTERNS = [
    r"^\?+$",
    r"^!+$",
    r"^[^\w\s]{2,}$",
]

DIRECT_ANSWER_PATTERNS = [
    r"直接给我答案",
    r"直接告诉我",
    r"给我完整答案",
    r"把答案给我",
    r"直接给代码",
    r"给我完整代码",
    r"just give me the answer",
    r"give me the answer",
    r"give me the code",
    r"full code",
    r"complete solution",
]

CONCEPT_EXTRACTION_SYSTEM_PROMPT = """
You are a concept extraction module for an educational tutoring agent.

Extract explicit academic concepts, technical terms, task objects, algorithms,
programming constructs, or domain-specific ideas mentioned in the student's message.

Return ONLY valid JSON:
{
  "has_explicit_concepts": true,
  "concepts": ["concept 1", "concept 2"]
}

Rules:
1. Extract only concepts grounded in the student's message.
2. Prefer specific concepts over generic words.
3. Valid examples include:
   - "face recognition"
   - "neural network"
   - "algorithm"
   - "row-level trigger"
   - "linked list"
   - "decision tree"
4. Do not output debugging/meta words such as:
   - "json.dumps"
   - "indent"
   - "ensure_ascii"
   - "print"
   - "import"
5. If there are no clear concepts, return an empty list.
6. Output JSON only.
"""


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def looks_empty(text: str) -> bool:
    return len(text.strip()) == 0


def looks_nonsense(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True

    for pattern in NONSENSE_PATTERNS:
        if re.match(pattern, stripped):
            return True

    alnum_count = sum(ch.isalnum() for ch in stripped)
    if len(stripped) >= 4 and alnum_count / max(len(stripped), 1) < 0.2:
        return True

    return False


def asks_direct_answer(text: str) -> bool:
    t = normalize_text(text)
    return any(re.search(pattern, t) for pattern in DIRECT_ANSWER_PATTERNS)


def extract_json_object(raw_text: str) -> Optional[dict]:
    if not raw_text or not isinstance(raw_text, str):
        return None

    text = raw_text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            return None

    return None


def extract_simple_concepts_rule(text: str) -> List[str]:
    concept_keywords = [
        "face recognition",
        "facial recognition",
        "face detection",
        "neural network",
        "cnn",
        "convolutional neural network",
        "machine learning",
        "computer vision",
        "feature extraction",
        "classification",
        "opencv",
        "algorithm",
        "人脸识别",
        "人脸检测",
        "神经网络",
        "卷积神经网络",
        "算法",
        "特征提取",
        "分类",
        "row-level trigger",
        "statement-level trigger",
        "anonymous inner class",
        "linked list",
        "decision tree",
        "data mining",
        "digital twin",
        "blockchain",
        "recursion",
        "function",
        "trigger",
        "python",
        "sql",
        "java",
        "join",
        "loop",
        "array",
        "class",
        "iot",
        "hci",
        "nft",
        "project goal",
        "baseline",
        "evaluation metric",
        "preprocessing",
        "cross validation",
        "overfitting",
        "underfitting",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "auc",
        "rmse",
        "report",
        "interpretation",
    ]

    t = normalize_text(text)
    found: List[str] = []

    for keyword in sorted(concept_keywords, key=len, reverse=True):
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, t):
            found.append(keyword.lower())

    filtered: List[str] = []
    for keyword in found:
        if not any(keyword != other and keyword in other for other in found):
            filtered.append(keyword)

    return filtered


def extract_concepts_with_llm(text: str) -> List[str]:
    suspicious_markers = [
        "json.dumps",
        "ensure_ascii",
        "indent",
        '"diagnosis"',
        '"response"',
        '"routing"',
    ]
    lowered = text.lower()
    if any(marker in lowered for marker in suspicious_markers):
        return []

    raw_output = call_llm(CONCEPT_EXTRACTION_SYSTEM_PROMPT, f"Student message:\n{text}")
    data = extract_json_object(raw_output)
    if data is None:
        return []

    concepts = data.get("concepts", [])
    if not isinstance(concepts, list):
        return []

    banned_patterns = [
        r"json\.dumps",
        r"ensure_ascii",
        r"indent",
        r"print\(",
        r"def ",
        r"return ",
        r"import ",
    ]

    cleaned: List[str] = []
    for concept in concepts:
        if not isinstance(concept, str):
            continue
        value = concept.strip().lower()
        if not value:
            continue
        if any(re.search(pattern, value) for pattern in banned_patterns):
            continue
        cleaned.append(value)

    deduped: List[str] = []
    for concept in cleaned:
        if concept not in deduped:
            deduped.append(concept)

    return deduped


def extract_simple_concepts(text: str, use_llm: bool = True) -> List[str]:
    if use_llm:
        concepts = extract_concepts_with_llm(text)
        if concepts:
            return concepts
    return extract_simple_concepts_rule(text)