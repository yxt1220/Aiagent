def calculator_tool(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算失败: {str(e)}"


def search_tool(query: str) -> str:
    fake_database = {
        "python": "Python 是一种流行的编程语言。",
        "ai agent": "AI Agent 通常包含感知、规划、记忆、工具调用、行动等模块。",
        "rag": "RAG 是 Retrieval-Augmented Generation，检索增强生成。"
    }

    query_lower = query.lower()
    for key, value in fake_database.items():
        if key in query_lower:
            return value
    return f"没有找到关于 '{query}' 的结果。"


TOOLS = {
    "calculator": calculator_tool,
    "search": search_tool
}