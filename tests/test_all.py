"""非API模块测试"""
import sys
sys.path.insert(0, ".")

from storage.document_parser import parse_text
from storage.vector_store import add_documents, search, count
from storage.metadata_store import add_note, list_notes, count as meta_count
from memory.short_term import ShortTermMemory
from memory.long_term import add_topic, get_context_summary
from scheduler.forgetting_curve import record_access, calculate_retention, get_notes_for_review
from tools import add_knowledge, search_knowledge, manage_knowledge, reminder

print("=== 测试1: 文档解析 ===")
docs = parse_text("Python的GIL是全局解释器锁，它导致多线程无法真正并行", source="test")
print("分块数:", len(docs))
print("内容:", docs[0]["content"])

print("\n=== 测试2: 向量存储 ===")
add_documents(docs)
print("文档总数:", count())
results = search("多线程并行")
print("搜索结果数:", len(results))
if results:
    print("最相关:", results[0]["content"][:60])

print("\n=== 测试3: 元数据存储 ===")
note_id = add_note("Python GIL 测试笔记", tags=["Python", "GIL"], importance="high")
print("笔记ID:", note_id)
print("笔记总数:", meta_count())

print("\n=== 测试4: 短期记忆 ===")
mem = ShortTermMemory()
mem.add_message("user", "你好")
mem.add_message("assistant", "你好！")
print("消息数:", len(mem.get_messages()))

print("\n=== 测试5: 长期记忆 ===")
add_topic("Python", [note_id])
print("上下文摘要:", get_context_summary())

print("\n=== 测试6: 遗忘曲线 ===")
record_access(note_id)
retention = calculate_retention(note_id)
print("保留率:", retention)
reminders = get_notes_for_review()
print("需复习数:", len(reminders))

print("\n=== 测试7: 工具Schema ===")
schema = add_knowledge.get_schema()
print("add_knowledge:", schema["function"]["name"])
schema = search_knowledge.get_schema()
print("search_knowledge:", schema["function"]["name"])
schema = manage_knowledge.get_schema()
print("manage_knowledge:", schema["function"]["name"])
schema = reminder.get_schema()
print("reminder:", schema["function"]["name"])

print("\n=== 测试8: 工具执行(不依赖LLM) ===")
result = add_knowledge.execute({
    "content": "Redis使用LRU算法淘汰缓存数据，可以通过maxmemory-policy配置",
    "tags": ["Redis", "LRU", "缓存"],
    "importance": "high"
})
print("添加结果:", result)

result = search_knowledge.execute({"query": "Redis缓存淘汰", "top_k": 3})
print("搜索结果:", result[:100])

result = manage_knowledge.execute({"action": "count"})
print("笔记统计:", result)

result = reminder.execute({"threshold": 0.5})
print("提醒:", result[:100])

print("\n" + "=" * 50)
print("所有非API模块测试通过!")
print("=" * 50)
