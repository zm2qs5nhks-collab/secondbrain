#!/usr/bin/env python3
"""第二大脑 —— 知识图谱探索（REST 版，用法见 ../SKILL.md）"""
import os
import sys
import json
import argparse

import requests

BASE = os.getenv("SECOND_BRAIN_BASE_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("SECOND_BRAIN_TOKEN", "")


def main():
    ap = argparse.ArgumentParser(description="第二大脑知识图谱")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stats")
    sub.add_parser("discover")
    q = sub.add_parser("query")
    q.add_argument("node")
    q.add_argument("--max-hops", type=int, default=2)
    a = ap.parse_args()

    if not TOKEN:
        print("请先设置环境变量 SECOND_BRAIN_TOKEN", file=sys.stderr)
        sys.exit(2)

    payload = {"action": a.cmd}
    if a.cmd == "query":
        payload["node"] = a.node
        payload["max_hops"] = a.max_hops

    r = requests.post(
        f"{BASE}/api/knowledge_graph",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
