"""
网页内容抓取工具 —— 从URL提取文章正文
"""

import json
import re
import requests
from bs4 import BeautifulSoup


def get_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "fetch_web_content",
            "description": "从网页URL抓取文章内容并保存到知识库。当用户提供网址链接时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页URL",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "内容的标签/分类",
                    },
                },
                "required": ["url"],
            },
        },
    }


def fetch_url(url: str, timeout: int = 15) -> dict:
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
        text = text[:15000] + "\n\n... (内容已截断，共" + str(len(text)) + "字符)"

    return {"title": title, "content": text, "url": url, "length": len(text)}


def execute(arguments: dict, user_id: str = None) -> str:
    url = arguments.get("url", "")
    tags = arguments.get("tags", [])

    if not url.strip():
        return json.dumps({"error": "URL不能为空"}, ensure_ascii=False)

    try:
        result = fetch_url(url)
    except Exception as e:
        return json.dumps({"error": f"抓取失败: {str(e)}"}, ensure_ascii=False)

    if not result["content"].strip():
        return json.dumps({"error": "未能提取到有效内容"}, ensure_ascii=False)

    from tools.add_knowledge import execute as add_exec
    add_result = json.loads(add_exec({
        "content": f"[来源: {result['title'] or result['url']}]\n\n{result['content']}",
        "tags": tags if tags else ["网页收藏"],
        "importance": "normal",
    }, user_id=user_id))

    if not add_result.get("note_id"):
        return json.dumps({
            "error": f"保存失败: {add_result.get('error', '未知错误')}",
            "debug": {
                "title": result["title"],
                "content_length": result["length"],
                "add_result": add_result,
            },
        }, ensure_ascii=False)

    return json.dumps({
        "status": "success",
        "title": result["title"],
        "url": result["url"],
        "content_length": result["length"],
        "chunks_stored": add_result.get("chunks_stored", 0),
        "note_id": add_result.get("note_id"),
        "message": f"网页内容已保存（{result['length']}字符，{add_result.get('chunks_stored', 0)}个分块）",
    }, ensure_ascii=False)
