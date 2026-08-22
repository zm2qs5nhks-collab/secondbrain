"""
在线搜索工具 —— 百度搜索 + 一键入库
"""

import re
import json
import requests
from bs4 import BeautifulSoup


def web_search(query: str, max_results: int = 8) -> list[dict]:
    """百度搜索并返回结果列表"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(
            "https://www.baidu.com/s",
            params={"wd": query, "rn": max_results},
            headers=headers,
            timeout=10,
        )
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for item in soup.select(".result, .c-container"):
            title_tag = item.select_one("h3 a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = title_tag.get("href", "")

            abstract_tag = item.select_one(".c-abstract, .content-right_2s-H4, span[class*='content']")
            snippet = abstract_tag.get_text(strip=True) if abstract_tag else ""

            if title:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                })

        return results[:max_results] if results else [{"error": "未找到结果"}]
    except Exception as e:
        return [{"error": str(e)}]
