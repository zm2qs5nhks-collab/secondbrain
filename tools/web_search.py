"""
在线搜索工具 —— 百度搜索 + 一键入库
"""

import re
import json
import requests
from bs4 import BeautifulSoup


def fetch_url_content(url: str, timeout: int = 15) -> dict:
    """抓取网页并提取正文"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    title = ""
    if soup.title:
        title = soup.title.get_text(strip=True)

    for tag in soup(["script", "style", "nav", "footer", "header",
                      "aside", "iframe", "noscript"]):
        tag.decompose()

    article = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"content|article|post|entry", re.I))
        or soup.find("div", id=re.compile(r"content|article|post|entry", re.I))
        or soup.body
    )

    if article is None:
        text = soup.get_text(separator="\n", strip=True)
    else:
        text = article.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    text = "\n".join(lines)

    if len(text) > 15000:
        text = text[:15000] + "\n\n... (内容已截断)"

    return {"title": title, "content": text, "url": url, "length": len(text)}
