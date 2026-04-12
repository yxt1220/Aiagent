from app.agent import TutorAgent
from app.layers.file_ingestion.file_registry import file_registry

agent = TutorAgent()

WELCOME_MESSAGE = "你好！我是你的 Scaffolding Tutor。你可以上传数据文件，然后告诉我你想做什么，我会一步一步引导你。"


def handle_chat(message: str, session_id: str | None = None, context: str = "") -> dict:
    # ── 空消息 = 初始化 / New Session → reset + 返回欢迎语 ──
    if not message or not message.strip():
        agent.reset_episode()
        file_registry.clear_files("default-session")
        return {
            "response": WELCOME_MESSAGE,
            "diagnosis": None,
            "routing": None,
            "retrieval": None,
            "pedagogical_control": {"hint_level": "L1", "strategy": "greeting"},
            "episode_state": {"phase": "diagnose", "turn_count": 0, "mastery_signals": 0},
        }

    # ── 正常消息 ──
    effective_session_id = session_id or "default-session"

    file_context = file_registry.get_combined_context(effective_session_id)
    if file_context:
        context = f"{context}\n\n{file_context}".strip()

    result = agent.run(
        user_input=message,
        context=context
    )
    print(result)

    return result
