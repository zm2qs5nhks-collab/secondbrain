#!/usr/bin/env python3
"""第二大脑 —— 待复习清单（REST 版，用法见 ../SKILL.md）"""
import os
import sys
import argparse

import requests

BASE = os.getenv("SECOND_BRAIN_BASE_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("SECOND_BRAIN_TOKEN", "")


def main():
    ap = argparse.ArgumentParser(description="第二大脑待复习清单")
    ap.add_argument("--threshold", type=float, default=0.5)
    a = ap.parse_args()

    if not TOKEN:
        print("请先设置环境变量 SECOND_BRAIN_TOKEN", file=sys.stderr)
        sys.exit(2)

    r = requests.post(
        f"{BASE}/api/reminders",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"threshold": a.threshold},
        timeout=60,
    )
    data = r.json()
    for it in data.get("reminders", []):
        print(f"[{it.get('urgency')}] 留存 {it.get('retention')}  {it.get('preview')}")
    print("共", data.get("total", 0), "条")


if __name__ == "__main__":
    main()
