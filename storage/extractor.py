"""
LLM 实体关系抽取器
"""

import json
from agent.llm import chat_completion


def extract_json(text: str) -> dict | list:
    """从 LLM 输出中提取 JSON"""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


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
    """规范化抽取结果：补全 category、去重"""
    if not isinstance(result, dict):
        return {"entities": [], "relations": []}
    entities = result.get("entities", []) or []
    relations = []
    for r in result.get("relations", []) or []:
        if not isinstance(r, dict):
            continue
        cat = (r.get("category") or "").strip().lower()
        if cat not in VALID_CATEGORIES:
            cat = infer_category(r.get("relation", ""))
        relations.append({
            "source": r.get("source", ""),
            "relation": r.get("relation", "关联"),
            "target": r.get("target", ""),
            "category": cat,
        })
    return {"entities": entities, "relations": relations}


def extract_from_text(text: str) -> dict:
    """从文本中抽取实体和关系"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请从以下笔记中提取实体和关系：\n\n{text}"},
    ]
    response = chat_completion(messages)
    return _normalize(extract_json(response["content"]))


def extract_from_notes(notes: list[dict]) -> dict:
    """批量抽取，返回合并后的实体和关系"""
    all_entities = {}
    all_relations = []

    for note in notes:
        content = note.get("content", "")
        if not content:
            continue
        result = extract_from_text(content)

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
