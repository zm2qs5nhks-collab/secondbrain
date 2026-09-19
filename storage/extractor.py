"""
LLM 实体关系抽取器
"""

import json
import re
from agent.llm import chat_completion


def extract_json(text: str) -> dict | list:
    """从 LLM 输出中稳健地提取 JSON（容忍 ```json 包裹、前后废话）"""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    for op, cl in (("{", "}"), ("[", "]")):
        i, j = text.find(op), text.rfind(cl)
        if i != -1 and j != -1 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except Exception:
                continue
    raise ValueError("无法从模型输出中解析 JSON")


SYSTEM_PROMPT = """你是一个知识图谱构建专家。你的任务是从笔记文本中提取实体和关系，并给每条关系标注「类别」。

规则：
1. 实体类型：技术、概念、人物、场景、方法、工具、框架、事件、指标 等
2. 每条关系必须带一个 category，只能是以下之一：
   - hierarchy  层级/分类：属于、包含、是一种、分为、子类、父类、上位、下位、组成
   - temporal   时序/发展：先于、之后、之前、随后、发展、演进、演变、源于、起源
   - causal     因果：导致、因为、由于、引起、解决、避免、使得、所以、原因、结果、依赖
   - sequential 流程/步骤：首先、然后、接着、下一步、最后、依次、步骤、流程
   - assoc      其它关联：应用于、对比、使用、相关 等
3. 实体名称要标准化（如 "Redis" 不要写成 "redis数据库"）
4. 只提取有明确语义关系的实体对，不要强行建立关系
5. 输出严格的 JSON 格式

输出格式：
{
  "entities": [
    {"name": "实体名", "type": "实体类型"}
  ],
  "relations": [
    {"source": "源实体", "relation": "关系短语", "target": "目标实体", "category": "hierarchy|temporal|causal|sequential|assoc"}
  ]
}"""

VALID_CATEGORIES = {"hierarchy", "temporal", "causal", "sequential", "assoc"}

# 关系短语 → 类别 的关键词兜底（旧数据 / LLM 漏标时使用）
CATEGORY_KEYWORDS = {
    "hierarchy": ["属于", "包含", "是一种", "分为", "子类", "父类", "上位", "下位", "组成", "分类", "部分"],
    "temporal": ["先于", "之后", "之前", "随后", "发展", "演进", "演变", "源于", "起源", "然后"],
    "causal": ["导致", "因为", "由于", "引起", "解决", "避免", "使得", "所以", "原因", "结果", "依赖", "促成"],
    "sequential": ["首先", "然后", "接着", "下一步", "最后", "依次", "步骤", "流程", "顺序"],
}


def infer_category(relation: str) -> str:
    """根据关系短语推断类别（兜底）"""
    r = relation or ""
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in r for k in kws):
            return cat
    return "assoc"


def _normalize(result: dict) -> dict:
    """规范化抽取结果：补全 category、校验实体、去重"""
    if not isinstance(result, dict):
        return {"entities": [], "relations": []}
    ents = []
    seen = set()
    for e in (result.get("entities", []) or []):
        if not isinstance(e, dict):
            continue
        name = str(e.get("name", "")).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        ents.append({"name": name, "type": str(e.get("type", "未知") or "未知")})
    relations = []
    for r in (result.get("relations", []) or []):
        if not isinstance(r, dict):
            continue
        src = str(r.get("source", "")).strip()
        tgt = str(r.get("target", "")).strip()
        if not src or not tgt:
            continue
        cat = (r.get("category") or "").strip().lower()
        if cat not in VALID_CATEGORIES:
            cat = infer_category(r.get("relation", ""))
        relations.append({
            "source": src,
            "relation": str(r.get("relation", "关联") or "关联"),
            "target": tgt,
            "category": cat,
        })
    return {"entities": ents, "relations": relations}


_ENT_RE = re.compile(r'\{\s*"name"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"type"\s*:\s*"((?:[^"\\]|\\.)*)"', re.S)
_REL_RE = re.compile(
    r'\{\s*"source"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"relation"\s*:\s*"((?:[^"\\]|\\.)*)"'
    r'\s*,\s*"target"\s*:\s*"((?:[^"\\]|\\.)*)"', re.S)


def _salvage(text: str) -> dict:
    """从（可能被截断的）模型输出里抢救出完整的实体/关系对象"""
    text = text or ""
    ents = [{"name": n, "type": t} for n, t in _ENT_RE.findall(text)]
    rels = [{"source": s, "relation": r, "target": t} for s, r, t in _REL_RE.findall(text)]
    return {"entities": ents, "relations": rels}


def extract_from_text(text: str, user_id: str = None) -> dict:
    """从文本中抽取实体和关系（user_id 用于选用该用户配置的模型）"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请从以下笔记中提取实体和关系：\n\n{text}"},
    ]
    raw = ""
    for _ in range(2):  # 空内容重试一次
        response = chat_completion(messages, user_id=user_id)
        raw = (response.get("content") or "").strip()
        if raw:
            break
    if not raw:
        raise ValueError("模型返回了空内容（可能被内容过滤或超时）")

    parsed = None
    try:
        parsed = extract_json(raw)
    except Exception:
        parsed = None

    if parsed is not None:
        result = _normalize(parsed)
        if result["entities"]:
            return result

    # 解析失败 / 没抽到实体 → 从原始输出里抢救（应对 JSON 被截断）
    salv = _salvage(raw)
    if salv["entities"] or salv["relations"]:
        return _normalize(salv)
    if parsed is not None:
        return _normalize(parsed)
    raise ValueError(f"模型输出无法解析为 JSON；原始输出前 300 字：{raw[:300]}")


def extract_from_notes(notes: list[dict], user_id: str = None) -> dict:
    """批量抽取，返回合并后的实体和关系"""
    all_entities = {}
    all_relations = []

    for note in notes:
        content = note.get("content", "")
        if not content:
            continue
        result = extract_from_text(content, user_id=user_id)

        for entity in result.get("entities", []):
            key = entity["name"]
            if key not in all_entities:
                all_entities[key] = entity

        for rel in result.get("relations", []):
            all_relations.append(rel)

    return {
        "entities": list(all_entities.values()),
        "relations": all_relations,
    }
