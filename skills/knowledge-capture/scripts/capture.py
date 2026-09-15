#!/usr/bin/env python3
"""第二大脑 —— 知识捕获（REST 版，用法见 ../SKILL.md）"""
import os
import sys
import argparse

import requests

BASE = os.getenv("SECOND_BRAIN_BASE_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("SECOND_BRAIN_TOKEN", "")


def _headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def main():
    ap = argparse.ArgumentParser(description="第二大脑知识捕获")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("text", help="保存一段文本/笔记")
    t.add_argument("content")
    t.add_argument("--tags", nargs="*", default=[])
    t.add_argument("--importance", default="normal", choices=["high", "normal", "low"])

    u = sub.add_parser("url", help="抓取网页并入库")
    u.add_argument("url")

    a = ap.parse_args()
    if not TOKEN:
        print("请先设置环境变量 SECOND_BRAIN_TOKEN", file=sys.stderr)
        sys.exit(2)

    if a.cmd == "text":
        r = requests.post(
            f"{BASE}/api/add_note",
            headers=_headers(),
            json={"content": a.content, "tags": a.tags, "importance": a.importance},
            timeout=60,
        )
    else:
        r = requests.post(
            f"{BASE}/api/fetch_web", headers=_headers(), json={"url": a.url}, timeout=90
        )

    print(r.status_code, r.text)


if __name__ == "__main__":
    main()
