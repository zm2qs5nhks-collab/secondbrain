"""
Agent 核心循环 —— ReAct 模式实现
"""

import json
from agent.llm import chat_completion
from agent.prompt import SYSTEM_PROMPT
from memory.short_term import ShortTermMemory
from memory import long_term
from tools import add_knowledge, search_knowledge, manage_knowledge, reminder, fetch_web
from tools import knowledge_graph_tool
import config


class SecondBrainAgent:
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.memory = ShortTermMemory()
        self.tools = {
            "add_knowledge": add_knowledge,
            "search_knowledge": search_knowledge,
            "manage_knowledge": manage_knowledge,
            "send_reminder": reminder,
            "fetch_web_content": fetch_web,
            "knowledge_graph": knowledge_graph_tool,
        }
        self.tool_schemas = [
            add_knowledge.get_schema(),
            search_knowledge.get_schema(),
            manage_knowledge.get_schema(),
            reminder.get_schema(),
            fetch_web.get_schema(),
            knowledge_graph_tool.get_schema(),
        ]

    def run(self, user_input: str) -> str:
        self.memory.add_message("user", user_input)

        long_term_context = long_term.get_context_summary(user_id=self.user_id)
        system_msg = SYSTEM_PROMPT + "\n\n" + long_term_context

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(self.memory.get_messages())

        for _ in range(config.AGENT_MAX_ITERATIONS):
            response = chat_completion(messages, tools=self.tool_schemas)

            if response.get("tool_calls"):
                tool_calls = response["tool_calls"]

                assistant_msg = {"role": "assistant", "content": None,
                                 "tool_calls": [
                                     {"id": tc["id"], "type": "function",
                                      "function": {"name": tc["name"],
                                                    "arguments": json.dumps(tc["arguments"], ensure_ascii=False)}}
                                     for tc in tool_calls
                                 ]}
                messages.append(assistant_msg)
                self.memory.add_tool_call(assistant_msg)

                for tc in tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["arguments"]
                    if tool_name in self.tools:
                        result = self.tools[tool_name].execute(tool_args, user_id=self.user_id)
                    else:
                        result = json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)

                    tool_msg = {"role": "tool", "tool_call_id": tc["id"],
                                "content": result}
                    messages.append(tool_msg)
                    self.memory.add_tool_result(tc["id"], result)
            else:
                final_answer = response.get("content", "抱歉，我没有生成回答。")
                self.memory.add_message("assistant", final_answer)
                return final_answer

        return "抱歉，处理步骤过多，请简化您的问题后重试。"

    def chat(self, user_input: str) -> str:
        return self.run(user_input)
