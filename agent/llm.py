"""
LLM 调用封装
"""

import time
import json
from openai import OpenAI
import config


_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
    return _client


def chat_completion(messages: list[dict], tools: list[dict] = None,
                    max_retries: int = 3) -> dict:
    client = get_client()
    kwargs = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            msg = response.choices[0].message
            result = {"content": msg.content, "tool_calls": None}
            if msg.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                    }
                    for tc in msg.tool_calls
                ]
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"[LLM] 调用失败: {e}, {wait}秒后重试...")
                time.sleep(wait)
            else:
                raise


def get_embedding(text: str) -> list[float]:
    client = get_client()
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding
