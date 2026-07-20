"""
短期记忆 —— 对话历史管理 (保持内存，会话级)
"""

class ShortTermMemory:
    def __init__(self, max_messages: int = 50):
        self.messages: list[dict] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[:10] + self.messages[-30:]

    def add_tool_call(self, assistant_msg: dict):
        self.messages.append(assistant_msg)

    def add_tool_result(self, tool_call_id: str, content: str):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })

    def get_messages(self) -> list[dict]:
        return list(self.messages)

    def clear(self):
        self.messages = []

    def get_recent(self, n: int = 10) -> list[dict]:
        return self.messages[-n:]
