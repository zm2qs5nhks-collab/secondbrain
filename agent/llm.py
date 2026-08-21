"""
LLM 调用封装
"""

import time
import json
from openai import OpenAI
import config

_clients = {}
_settings = {}


def set_user_settings(user_id: str, api_key: str = None, base_url: str = None,
                      model_name: str = None, embedding_model: str = None):
    _settings[user_id] = {
        "api_key": api_key or config.OPENAI_API_KEY,
        "base_url": base_url or config.OPENAI_BASE_URL,
        "model_name": model_name or config.MODEL_NAME,
        "embedding_model": embedding_model or config.EMBEDDING_MODEL,
    }
    _clients.pop(user_id, None)


def _get_settings(user_id: str = None) -> dict:
    if user_id and user_id in _settings:
        return _settings[user_id]
    return {
        "api_key": config.OPENAI_API_KEY,
        "base_url": config.OPENAI_BASE_URL,
        "model_name": config.MODEL_NAME,
        "embedding_model": config.EMBEDDING_MODEL,
    }


def get_client(user_id: str = None) -> OpenAI:
    key = user_id or "__default__"
    if key not in _clients:
        s = _get_settings(user_id)
        _clients[key] = OpenAI(api_key=s["api_key"], base_url=s["base_url"])
    return _clients[key]


def chat_completion(messages: list[dict], tools: list[dict] = None,
                    max_retries: int = 3, user_id: str = None) -> dict:
    client = get_client(user_id)
    s = _get_settings(user_id)
    kwargs = {
        "model": s["model_name"],
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


def get_embedding(text: str, user_id: str = None, max_retries: int = 3) -> list[float]:
    client = get_client(user_id)
    s = _get_settings(user_id)
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(
                model=s["embedding_model"],
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"[Embedding] 调用失败: {e}, {wait}秒后重试...")
                time.sleep(wait)
            else:
                raise
