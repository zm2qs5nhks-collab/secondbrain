"""
进程内滑动窗口限流。

用途：登录爆破防护（Streamlit 登录页 + REST /api/auth/login）。

说明：
- 当前部署是「单进程」（一个 streamlit、一个 uvicorn），进程内计数够用；
- 如果以后上多 worker / 多实例，需要换成 Redis 之类的共享存储；
- 线程安全（Streamlit 每个会话一个线程，会用同一个字典）。
"""

import threading
import time

_LOCK = threading.Lock()
_HITS: dict[str, list[float]] = {}

# 超过这个 key 数量时做一次清理，防止被随机 key 撑爆内存
_MAX_KEYS = 20000


def check(key: str, limit: int = 5, window: int = 300) -> tuple[bool, int]:
    """记录一次尝试并判断是否放行。

    返回 (是否允许, 需等待秒数)。
    """
    now = time.time()
    with _LOCK:
        bucket = [t for t in _HITS.get(key, ()) if now - t < window]

        if len(bucket) >= limit:
            retry_after = int(window - (now - bucket[0])) + 1
            _HITS[key] = bucket
            return False, retry_after

        bucket.append(now)
        _HITS[key] = bucket

        if len(_HITS) > _MAX_KEYS:
            for k in [k for k, v in _HITS.items() if not v or now - v[-1] > window]:
                _HITS.pop(k, None)

        return True, 0


def reset(key: str) -> None:
    """登录成功后清空该 key 的失败计数。"""
    with _LOCK:
        _HITS.pop(key, None)


def cleanup(window: int = 300) -> int:
    """手动清理过期 key，返回清理数量（便于巡检脚本调用）。"""
    now = time.time()
    with _LOCK:
        stale = [k for k, v in _HITS.items() if not v or now - v[-1] > window]
        for k in stale:
            _HITS.pop(k, None)
        return len(stale)
