from app.layers.diagnosis.diagnosis_schema import DiagnosisResult


def apply_routing_rules(diagnosis: DiagnosisResult):
    concepts_text = " ".join(diagnosis.detected_concepts or []).lower()
    intent = (diagnosis.intent or "").lower()
    problem_type = (diagnosis.problem_type or "").lower()
    student_state = (diagnosis.student_state or "").lower()

    if diagnosis.is_nonsense:
        return {
            "route": "clarify",
            "reason": "Input is nonsense or unreadable.",
            "need_retrieval": False,
            "retrieval_mode": None,
            "response_mode": "ask_clarification",
            "escalate_to_pedagogy": False,
            "terminate_episode": False,
            "priority": "high",
            "recommended_next_step": "ask student to restate the question clearly",
            "notes": ["Do not retrieve content for nonsense input."],
            "target_chapter": None,
            "target_section_types": None,
        }

    if diagnosis.is_off_topic:
        return {
            "route": "off_topic",
            "reason": "Student input is off-topic.",
            "need_retrieval": False,
            "retrieval_mode": None,
            "response_mode": "redirect_to_task",
            "escalate_to_pedagogy": False,
            "terminate_episode": False,
            "priority": "medium",
            "recommended_next_step": "gently redirect student back to learning task",
            "notes": ["Keep response brief."],
            "target_chapter": None,
            "target_section_types": None,
        }

    if diagnosis.needs_clarification:
        return {
            "route": "clarify",
            "reason": "Diagnosis indicates clarification is needed before meaningful guidance.",
            "need_retrieval": False,
            "retrieval_mode": None,
            "response_mode": "ask_clarification",
            "escalate_to_pedagogy": False,
            "terminate_episode": False,
            "priority": "high",
            "recommended_next_step": "ask a focused clarification question",
            "notes": ["Do not overload student with explanation yet."],
            "target_chapter": None,
            "target_section_types": None,
        }

    if diagnosis.asks_for_direct_answer:
        return {
            "route": "controlled_help",
            "reason": "Student explicitly asks for direct answer; must enforce scaffolding policy.",
            "need_retrieval": True,
            "retrieval_mode": "light",
            "response_mode": "controlled_scaffold",
            "escalate_to_pedagogy": True,
            "terminate_episode": False,
            "priority": "high",
            "recommended_next_step": "retrieve minimal relevant support and respond with guided help only",
            "notes": ["Do not provide full solution."],
            "target_chapter": None,
            "target_section_types": ["Tips for Scaffolding Chatbot", "Socratic Question Prompts"],
        }

    if (
        intent in ["ask_explanation", "verify_answer", "ask_hint", "unknown"]
        and any(k in concepts_text for k in [
            "algorithm", "algorithms", "算法", "method", "methods", "model", "models",
            "neural network", "神经网络", "cnn", "svm", "knn",
            "classification", "regression", "face recognition", "人脸识别",
            "computer vision", "face detection", "imbalanced", "imbalance"
        ])
    ):
        return {
            "route": "retrieve_then_scaffold",
            "reason": "Method-selection / model-planning question maps to Chapter 4.",
            "need_retrieval": True,
            "retrieval_mode": "procedure",
            "response_mode": "step_guidance",
            "escalate_to_pedagogy": True,
            "terminate_episode": False,
            "priority": "high",
            "recommended_next_step": "retrieve Chapter 4 method-selection scaffolding",
            "notes": ["Use Chapter 4 first."],
            "target_chapter": 4,
            "target_section_types": [
                "Guiding Questions",
                "Examples of Methods by Task",
                "Typical Mistakes",
                "Tips for Scaffolding Chatbot",
                "Socratic Question Prompts",
            ],
        }

    if any(k in concepts_text for k in [
        "preprocessing", "imputation", "scaling", "normalization",
        "train test split", "cross validation", "data leakage"
    ]):
        return {
            "route": "retrieve_then_scaffold",
            "reason": "Preprocessing question maps to Chapter 3.",
            "need_retrieval": True,
            "retrieval_mode": "procedure",
            "response_mode": "step_guidance",
            "escalate_to_pedagogy": True,
            "terminate_episode": False,
            "priority": "medium",
            "recommended_next_step": "retrieve preprocessing guidance",
            "notes": ["Use Chapter 3 first."],
            "target_chapter": 3,
            "target_section_types": [
                "Guiding Questions",
                "Typical Mistakes",
                "Cognitive Misconceptions",
                "Tips for Scaffolding Chatbot",
            ],
        }

    if any(k in concepts_text for k in [
        "accuracy", "precision", "recall", "f1", "auc", "rmse",
        "evaluation", "compare models", "best model"
    ]):
        return {
            "route": "retrieve_then_scaffold",
            "reason": "Evaluation / comparison question maps to Chapter 6.",
            "need_retrieval": True,
            "retrieval_mode": "concept",
            "response_mode": "scaffolded_explanation",
            "escalate_to_pedagogy": True,
            "terminate_episode": False,
            "priority": "medium",
            "recommended_next_step": "retrieve evaluation guidance",
            "notes": ["Use Chapter 6 first."],
            "target_chapter": 6,
            "target_section_types": [
                "Guiding Questions",
                "Typical Mistakes",
                "Tips for Scaffolding Chatbot",
                "Socratic Question Prompts",
            ],
        }

    if student_state in ["frustrated", "stuck"]:
        return {
            "route": "support_then_scaffold",
            "reason": "Student appears frustrated or stuck; acknowledge state before teaching.",
            "need_retrieval": True,
            "retrieval_mode": "light",
            "response_mode": "affective_scaffold",
            "escalate_to_pedagogy": True,
            "terminate_episode": False,
            "priority": "high",
            "recommended_next_step": "acknowledge difficulty, then give smaller guided support",
            "notes": ["Reduce cognitive load."],
            "target_chapter": None,
            "target_section_types": ["Tips for Scaffolding Chatbot", "Socratic Question Prompts"],
        }

    if problem_type == "meta":
        return {
            "route": "meta_support",
            "reason": "Meta-level support should guide learning strategy.",
            "need_retrieval": True,
            "retrieval_mode": "light",
            "response_mode": "meta_guidance",
            "escalate_to_pedagogy": True,
            "terminate_episode": False,
            "priority": "medium",
            "recommended_next_step": "retrieve scaffolding tips",
            "notes": [],
            "target_chapter": None,
            "target_section_types": ["Tips for Scaffolding Chatbot", "Socratic Question Prompts"],
        }

    return None