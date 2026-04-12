from typing import Optional, Dict


TRIGGER_MATRIX = [
    {
        "chapter_number": 1,
        "section_types": [
            "Guiding Questions",
            "Expected Outputs",
            "Typical Mistakes",
            "Tips for Scaffolding Chatbot",
            "Socratic Question Prompts",
        ],
        "triggers": [
            "project goal", "scope", "problem formulation", "target variable",
            "evaluation metric", "baseline", "where to start", "project planning"
        ],
    },
    {
        "chapter_number": 2,
        "section_types": [
            "Guiding Questions",
            "Typical Mistakes",
            "Cognitive Misconceptions",
            "Tips for Scaffolding Chatbot",
        ],
        "triggers": [
            "eda", "outlier", "correlation", "distribution", "visualization",
            "data type", "missing values"
        ],
    },
    {
        "chapter_number": 3,
        "section_types": [
            "Guiding Questions",
            "Typical Mistakes",
            "Cognitive Misconceptions",
            "Tips for Scaffolding Chatbot",
        ],
        "triggers": [
            "preprocessing", "imputation", "scaling", "normalization",
            "train test split", "cross validation", "data leakage"
        ],
    },
    {
        "chapter_number": 4,
        "section_types": [
            "Guiding Questions",
            "Examples of Methods by Task",
            "Typical Mistakes",
            "Tips for Scaffolding Chatbot",
            "Socratic Question Prompts",
        ],
        "triggers": [
            "which method", "which model", "what algorithm", "what algorithms",
            "neural network", "cnn", "svm", "knn", "classification", "regression",
            "face recognition", "face detection", "computer vision", "algorithm choice",
            "method selection", "imbalanced", "imbalance"
        ],
    },
    {
        "chapter_number": 5,
        "section_types": [
            "Guiding Questions",
            "Typical Mistakes",
            "Tips for Scaffolding Chatbot",
            "Socratic Question Prompts",
        ],
        "triggers": [
            "hyperparameter", "parameter tuning", "overfitting", "underfitting",
            "optimizer", "learning rate", "model training"
        ],
    },
    {
        "chapter_number": 6,
        "section_types": [
            "Guiding Questions",
            "Typical Mistakes",
            "Tips for Scaffolding Chatbot",
            "Socratic Question Prompts",
        ],
        "triggers": [
            "accuracy", "precision", "recall", "f1", "auc", "rmse",
            "evaluation", "compare models", "best model"
        ],
    },
    {
        "chapter_number": 7,
        "section_types": [
            "Guiding Questions",
            "Typical Mistakes",
            "Tips for Scaffolding Chatbot",
            "Socratic Question Prompts",
        ],
        "triggers": [
            "interpretation", "report", "presentation", "conclusion", "limitations",
            "what do these results mean"
        ],
    },
]


def infer_chapter_from_text(text: str) -> Optional[Dict]:
    lowered = text.lower()
    best_match = None
    best_score = 0

    for entry in TRIGGER_MATRIX:
        score = sum(1 for trig in entry["triggers"] if trig in lowered)
        if score > best_score:
            best_score = score
            best_match = entry

    return best_match if best_score > 0 else None