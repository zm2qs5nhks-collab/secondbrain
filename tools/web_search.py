"""
在线搜索工具 —— LLM扩展查询 + 百度搜索 + 一键入库
"""

import re
import json
import requests
from bs4 import BeautifulSoup


def _expand_query(query: str, user_id: str = None) -> list[str]:
    """用 LLM 将模糊问题扩展为多个搜索关键词"""
    try:
        from agent.llm import chat_completion
        resp = chat_completion(
            messages=[
                {"role": "system", "content": (
                    "你是一个搜索助手。用户会给你一个模糊的问题或主题，"
                    "你要把它扩展成3-4个不同角度的百度搜索关键词，用JSON数组返回。"
                    "只返回数组，不要其他内容。"
                    "例如：用户输入'AI怎么学'，返回 [\"人工智能入门教程\", \"AI学习路线图\", \"深度学习基础知识\"]"
                )},
                {"role": "user", "content": query},
            ],
            user_id=user_id,
        )
        text = resp.get("content", "[]")
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            keywords = json.loads(match.group())
            return [query] + [k for k in keywords if k != query]
    except Exception:
        pass
    return [query]


def _baidu_search(query: str, max_results: int = 6) -> list[dict]:
    """单次百度搜索"""
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
        return results
    except Exception:
        return []


def web_search(query: str, max_results: int = 8, user_id: str = None) -> list[dict]:
    """扩展查询 + 多轮搜索 + 去重"""
    keywords = _expand_query(query, user_id=user_id)

    seen_urls = set()
    all_results = []
    for kw in keywords:
        results = _baidu_search(kw, max_results=5)
        for r in results:
            if r.get("url") and r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)
        if len(all_results) >= max_results:
            break

    return all_results[:max_results] if all_results else [{"error": "未找到结果"}]
