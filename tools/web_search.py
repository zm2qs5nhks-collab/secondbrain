"""
在线搜索工具 —— Bing 真实搜索（可解析） + 网页抓取入库
"""

import re
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

SEARCH_ENGINES = {
    "cn_bing": "https://cn.bing.com/search?q={query}&setlang=zh-hans",
    "global_bing": "https://www.bing.com/search?q={query}&setlang=zh-hans",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def search_web(query: str, count: int = 10, engine: str = "cn_bing") -> list[dict]:
    """使用 Bing 真实检索，返回解析后的结果列表（每项含 title / url / snippet）"""
    url_tpl = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["cn_bing"])
    url = url_tpl.format(query=urllib.parse.quote_plus(query))
    resp = requests.get(url, headers=HEADERS, timeout=12)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return parse_bing_results(resp.text, count=count)


def parse_bing_results(html: str, count: int = 10) -> list[dict]:
    """解析 Bing 搜索结果页（li.b_algo）"""
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for li in soup.select("li.b_algo"):
        if len(results) >= count:
            break
        a = li.select_one("h2 a")
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get("href", "").strip()
        if not href.startswith("http"):
            continue
        cite_el = li.select_one("cite")
        cite = cite_el.get_text(strip=True) if cite_el else ""
        p_el = li.select_one("p") or li.select_one("div.b_caption p") or li.select_one(".b_paractl")
        snippet = p_el.get_text(strip=True) if p_el else ""
        results.append({"title": title, "url": href, "cite": cite, "snippet": snippet})
    return results


def bing_search_iframe_url(query: str, engine: str = "cn_bing") -> str:
    """返回 Bing 搜索的 iframe 可嵌入 URL（Bing 允许被 iframe 加载）"""
    url_tpl = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["cn_bing"])
    return url_tpl.format(query=urllib.parse.quote_plus(query))


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
