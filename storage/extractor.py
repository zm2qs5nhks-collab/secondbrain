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


SYSTEM_PROMPT = """你是一个知识图谱构建专家。你的任务是从笔记文本中提取实体和关系。

规则：
1. 实体类型包括：技术、概念、人物、场景、方法、工具、框架等
2. 关系类型包括：应用于、依赖、属于、对比、解决、包含、使用等
3. 实体名称要标准化（如 "Redis" 不要写成 "redis数据库"）
4. 只提取有明确语义关系的实体对，不要强行建立关系
5. 输出严格的 JSON 格式

输出格式：
{
  "entities": [
    {"name": "实体名", "type": "实体类型"}
  ],
  "relations": [
    {"source": "源实体", "relation": "关系类型", "target": "目标实体"}
  ]
}"""


def extract_from_text(text: str) -> dict:
    """从文本中抽取实体和关系"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请从以下笔记中提取实体和关系：\n\n{text}"},
    ]
    response = chat_completion(messages)
    return extract_json(response["content"])


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
