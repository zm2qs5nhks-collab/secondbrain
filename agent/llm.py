"""
LLM 调用封装
"""

import json
import time
from openai import OpenAI
import config

_clients = {}
_settings = {}

_RATE_HINTS = ("429", "rate limit", "too many requests", "1302", "1305")


def _is_rate_limit(err: Exception) -> bool:
    m = str(err).lower()
    return any(h in m for h in _RATE_HINTS)


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
        _clients[key] = OpenAI(
            api_key=s["api_key"],
            base_url=s["base_url"],
            timeout=getattr(config, "LLM_TIMEOUT", 60),
            max_retries=getattr(config, "LLM_MAX_RETRIES", 1),
        )
    return _clients[key]


def chat_completion(messages: list[dict], tools: list[dict] = None,
                    user_id: str = None) -> dict:
    client = get_client(user_id)
    s = _get_settings(user_id)
    kwargs = {
        "model": s["model_name"],
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": getattr(config, "LLM_MAX_TOKENS", 4096),
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    # 429 限流自动重试（指数退避），避免整批抽取因为偶发限流全军覆没
    retries = int(getattr(config, "LLM_RATE_RETRIES", 3))
    response = None
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(**kwargs)
            break
        except Exception as e:
            if _is_rate_limit(e) and attempt < retries:
                time.sleep(min(3 * (attempt + 1), 15))
                continue
            raise
    if response is None:
        raise RuntimeError("LLM 调用失败：超过重试次数")

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


def get_embedding(text: str, user_id: str = None) -> list[float]:
    client = get_client(user_id)
    s = _get_settings(user_id)
    response = client.embeddings.create(
        model=s["embedding_model"],
        input=text,
    )
    return response.data[0].embedding
