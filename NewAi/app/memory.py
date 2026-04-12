class Memory:
    def __init__(self):
        self.history = []

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_context(self) -> str:
        lines = []
        for item in self.history:
            lines.append(f"{item['role']}: {item['content']}")
        return "\n".join(lines)

    def clear(self):
        self.history = []