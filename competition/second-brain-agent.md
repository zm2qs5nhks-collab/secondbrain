# 🧠 第二大脑 —— 个人知识管理 Agent

> 一个能读取你的笔记和文档，在你遗忘关键信息时主动提醒你，并帮你发现知识之间隐藏联系的 AI Agent。

---

## 目录

- [项目概述](#项目概述)
- [核心创新点](#核心创新点)
- [功能设计](#功能设计)
- [技术架构](#技术架构)
- [技术栈选型](#技术栈选型)
- [开发计划](#开发计划)
- [项目结构](#项目结构)
- [核心模块设计](#核心模块设计)
- [Agent 工作流程](#agent-工作流程)
- [记忆系统设计](#记忆系统设计)
- [主动推送机制](#主动推送机制)
- [Prompt 设计](#prompt-设计)
- [避坑指南](#避坑指南)
- [学习收获](#学习收获)

---

## 项目概述

### 痛点

现代人每天接触大量知识——文章、笔记、课程、灵感片段——但这些信息散落在各个平台，且随着时间推移逐渐遗忘。现有的知识管理工具（Notion、Obsidian、Logseq）都是**被动工具**：你必须主动搜索才能找到需要的内容。

### 解决方案

构建一个**主动型知识管理 Agent**，它能够：

1. 自动导入和理解你的知识内容
2. 在你需要时快速语义检索
3. 在你不需要时主动推送"你快忘了的重要知识"
4. 发现你不同笔记之间隐藏的关联

### 与现有产品的差异

| 产品 | 模式 | 局限 |
|------|------|------|
| Notion AI | 被动等待提问 | 不会主动提醒你任何事 |
| Obsidian | 关键词搜索 | 搜不到"意思相近但用词不同"的内容 |
| Logseq | 本地知识图谱 | 无记忆能力，无主动推送 |
| ChatGPT | 每次对话无状态 | 不记得你之前学过什么 |
| **本项目** | **主动推送 + 语义检索 + 长期记忆** | — |

---

## 核心创新点

### 创新一：从被动搜索到主动推送

```
传统模式：  用户想起某个知识 → 打开搜索 → 输入关键词 → 浏览结果
本项目：    Agent 发现你快忘了 → 主动推送 → "这个概念你3天没碰了，要复习吗？"
```

Agent 具备自主性——不需要用户触发就能行动。这是 Agent 与传统工具的根本区别。

### 创新二：知识关联发现

```
用户分别存了：
  - 笔记 A："Redis 的 LRU 淘汰策略"
  - 笔记 B："电商秒杀系统的架构设计"

Agent 主动发现：
  "笔记 A 和笔记 B 有潜在关联：Redis 的 LRU 策略可以用于
   秒杀系统的热点商品缓存淘汰，要我把这个关联整理成一段分析吗？"
```

Agent 具备推理能力——不只是检索，还能发现隐藏联系。

### 创新三：基于遗忘曲线的智能复习

```
Agent 记住：
  - 这个概念是什么时候学的
  - 用户复习了几次
  - 每次复习后的掌握程度

Agent 决策：
  - 学了1天没复习 → 高优先级推送
  - 学了7天复习过2次且掌握好 → 降低优先级
  - 学了30天完全没碰 → 紧急推送
```

Agent 具备记忆管理能力——不只是存储，还有衰减和优先级。

---

## 功能设计

### 功能一：知识入库（Tool: add_knowledge）

**描述：** 用户通过文件拖入或文字输入的方式，将知识内容导入系统。

**支持的输入方式：**

| 输入方式 | 格式 | 说明 |
|---------|------|------|
| 文本文件 | `.txt`, `.md` | 直接读取并解析 |
| 网页链接 | URL | 抓取正文内容（后期实现） |
| 文字输入 | 自然语言 | 用户直接说一句话，Agent 提取关键信息存储 |

**处理流程：**

```
输入内容
  → 文档解析（提取纯文本）
  → 文本分块（按语义段落切分）
  → 向量化（Embedding）
  → 存入向量数据库（附带元数据：时间、标签、来源）
  → 更新长期记忆（知识图谱）
```

### 功能二：知识检索（Tool: search_knowledge）

**描述：** 用户用自然语言提问，Agent 从知识库中找到最相关的内容并用 LLM 总结回答。

**示例：**

```
用户："我之前记过关于 Redis 的内容吗？"

Agent 内部流程：
  1. 将用户问题向量化
  2. 在 ChromaDB 中检索 top-5 最相似的文档块
  3. 将检索结果 + 用户问题一起传给 LLM
  4. LLM 生成总结性回答，并标注信息来源

Agent 回答：
  "你有3条关于 Redis 的笔记：
   1. 4月12日记录的 'Redis LRU 淘汰策略'（文件：notes/cache.md）
   2. 4月15日记录的 'Redis 分布式锁实现'（文件：notes/distributed.md）
   3. 4月20日记录的 'Redis 与 MySQL 缓存一致性'（文件：notes/cache.md）
   
   需要我详细展开哪一条？"
```

### 功能三：主动推送（Tool: send_reminder）

**描述：** Agent 定时扫描知识库，基于遗忘曲线算法识别"即将被遗忘的重要知识"，主动推送复习提醒。

**推送触发条件：**

| 条件 | 示例 |
|------|------|
| 遗忘曲线预警 | 某知识点超过 N 天未被访问，且重要性较高 |
| 知识关联发现 | 新入库的内容与已有内容存在语义关联 |
| 定期总结 | 每周自动生成"本周知识回顾" |

**推送内容示例：**

```
📢 知识提醒
你3天前学的「Redis 缓存策略」和今天刚存的「电商秒杀方案」
有很强的关联。Redis 的 LRU 淘汰策略可以直接应用于秒杀场景
的热点商品缓存管理。

要不要我把这个关联整理成一段分析？
[查看详情] [稍后提醒] [忽略]
```

### 功能四：对话式管理（Agent 自主决策）

**描述：** Agent 可以通过自然语言对话完成复杂的知识管理任务，自主决定调用哪些工具、按什么顺序。

**示例对话：**

```
用户："帮我总结一下这周学了什么"

Agent 内部决策：
  1. 调用 search_knowledge 检索最近7天的所有笔记
  2. 调用 LLM 对内容进行分类和总结
  3. 生成结构化的周报

Agent 回答：
  "本周你共记录了8条笔记，主要集中在3个主题：
   
   📌 Redis 缓存（3条）
     - LRU 淘汰策略、分布式锁、缓存一致性
   
   📌 系统设计（3条）
     - 秒杀架构、限流方案、消息队列
   
   📌 Python 进阶（2条）
     - GIL 全局锁、异步编程
   
   建议重点复习 Redis 缓存一致性，这是本周最复杂的内容。"
```

---

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户界面层                          │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │  命令行界面     │  │  Web 界面       │                │
│  │  (Week 1-3)    │  │  (Week 4)      │                 │
│  └───────┬────────┘  └───────┬────────┘                 │
│          └──────────┬────────┘                          │
│                     ▼                                    │
├─────────────────────────────────────────────────────────┤
│                    Agent 核心层                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              System Prompt                        │   │
│  │         （定义 Agent 角色、能力、行为规则）        │   │
│  ├──────────────────────────────────────────────────┤   │
│  │              LLM 推理引擎                         │   │
│  │         （OpenAI GPT / 本地 Ollama）              │   │
│  ├──────────────────────────────────────────────────┤   │
│  │           Tool Router（工具路由）                  │   │
│  │         根据用户意图选择合适的工具                 │   │
│  ├──────────────────────────────────────────────────┤   │
│  │           Agent Loop（ReAct 循环）                │   │
│  │         思考 → 行动 → 观察 → 循环                 │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
┌──────────────┐ ┌───────────┐ ┌──────────────┐
│  文档解析模块 │ │ 向量检索  │ │  记忆管理    │
│              │ │    模块   │ │     模块     │
└──────┬───────┘ └─────┬─────┘ └──────┬───────┘
       │               │              │
       ▼               ▼              ▼
┌──────────────┐ ┌───────────┐ ┌──────────────┐
│  本地文件系统 │ │ ChromaDB  │ │ JSON / SQLite│
│  (.md/.txt)  │ │ (向量库)  │ │  (记忆存储)  │
└──────────────┘ └───────────┘ └──────────────┘
```

### 数据流

```
用户输入
  │
  ▼
LLM 解析意图
  │
  ├── 意图：添加知识 ──→ 调用 add_knowledge
  │                        ├── 文档解析
  │                        ├── 文本分块
  │                        ├── 向量化
  │                        └── 存入 ChromaDB
  │
  ├── 意图：搜索知识 ──→ 调用 search_knowledge
  │                        ├── 向量检索 (top-k)
  │                        ├── LLM 总结
  │                        └── 返回回答
  │
  ├── 意图：知识管理 ──→ 调用 manage_knowledge
  │                        ├── 列出/删除/更新笔记
  │                        └── 返回结果
  │
  └── 意图：闲聊/其他 ──→ 直接用 LLM 回答
```

---

## 技术栈选型

| 组件 | 选择 | 版本 | 选择理由 |
|------|------|------|---------|
| 编程语言 | Python | 3.10+ | AI 生态最丰富，社区支持最好 |
| LLM API | OpenAI GPT-4o-mini | - | 性价比最高，Function Calling 支持好 |
| 本地 LLM（备选） | Ollama + Qwen2 | - | 免费，无 API 限制，适合调试 |
| 向量数据库 | ChromaDB | 0.4+ | 嵌入式，无需部署，Python 原生 |
| 文本分块 | LangChain | 0.2+ | 成熟的 Document Loader 和 Text Splitter |
| Embedding 模型 | text-embedding-3-small | - | OpenAI 官方，效果好成本低 |
| 定时任务 | APScheduler | 3.10+ | 轻量级，支持 cron 表达式 |
| Web 界面（第4周） | Streamlit | 1.30+ | 极简 Web 框架，Python 纯写 |
| 数据存储 | JSON / SQLite | - | 简单可靠，无需额外服务 |

### 安装依赖

```bash
pip install openai chromadb langchain langchain-community apscheduler streamlit
```

### 环境变量配置

```bash
# .env 文件
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1   # 可选，使用代理时修改
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

---

## 开发计划

### 总览

| 阶段 | 时间 | 核心目标 | 里程碑 |
|------|------|---------|--------|
| Week 1 | Day 1-7 | 基础搭建 | 能问"我的笔记里有什么关于XX的内容"并得到回答 |
| Week 2 | Day 8-14 | Agent 核心 | Agent 能自主决定"先搜索再回答"还是"直接回答" |
| Week 3 | Day 15-21 | 主动推送 | Agent 能主动推送"你该复习这个了" |
| Week 4 | Day 22-30 | 打磨演示 | 完整可演示的产品 |

### Week 1：基础搭建

| 天数 | 任务 | 具体内容 |
|------|------|---------|
| Day 1 | 项目初始化 | 创建项目结构、配置环境变量、调通 OpenAI API 调用 |
| Day 2 | 文档解析 | 实现 TXT/Markdown 文件读取、文本分块逻辑 |
| Day 3 | 向量化存储 | 集成 ChromaDB，实现文档向量化和持久化存储 |
| Day 4 | 语义检索 | 实现 query → embedding → 检索 → 返回 top-k 的完整链路 |
| Day 5 | RAG 回答 | 将检索结果注入 LLM prompt，生成总结性回答 |
| Day 6 | 命令行交互 | 实现基础的命令行 REPL 循环 |
| Day 7 | 集成测试 | 测试"添加笔记 → 搜索 → 回答"的完整流程 |

**Week 1 验收标准：**

```bash
$ python main.py
🧠 第二大脑 Agent 已启动！输入 'quit' 退出。

> 添加笔记：我把今天学的 Redis LRU 策略记下来了
✅ 已保存到知识库（ID: note_001）

> 我之前学过什么关于 Redis 的内容？
🔍 找到2条相关笔记：
  1. Redis LRU 淘汰策略（note_001）
  2. Redis 基础命令（note_005）
  
  你之前学过 Redis 的基本操作和 LRU 淘汰策略。
  LRU（Least Recently Used）是最常用的缓存淘汰算法...
```

### Week 2：Agent 核心

| 天数 | 任务 | 具体内容 |
|------|------|---------|
| Day 8 | Tool 定义 | 定义所有工具的 JSON Schema（add, search, list, delete） |
| Day 9 | Function Calling | 集成 OpenAI Function Calling，实现工具自动调用 |
| Day 10 | Agent Loop | 实现 ReAct 模式：思考 → 调用工具 → 观察结果 → 继续思考 |
| Day 11 | 短期记忆 | 实现对话历史管理，控制 context window 大小 |
| Day 12 | 长期记忆 | 实现用户偏好存储（常用标签、关注领域、学习节奏） |
| Day 13 | 元数据管理 | 为每条笔记添加时间、标签、访问次数等元数据 |
| Day 14 | 联调测试 | 测试 Agent 自主决策的完整流程 |

**Week 2 验收标准：**

```
> 帮我整理一下关于系统设计的笔记
Agent 内部决策链：
  1. [思考] 用户想看系统设计相关的笔记，我需要先搜索
  2. [行动] 调用 search_knowledge(query="系统设计", top_k=10)
  3. [观察] 找到5条相关笔记
  4. [思考] 内容较多，我需要分类整理后呈现
  5. [回答] "找到5条系统设计笔记，分为3类：..."
```

### Week 3：主动推送

| 天数 | 任务 | 具体内容 |
|------|------|---------|
| Day 15 | 遗忘曲线算法 | 实现基于间隔重复的遗忘曲线计算 |
| Day 16 | 定时扫描 | 用 APScheduler 实现每日定时扫描知识库 |
| Day 17 | 推送决策 | 根据遗忘曲线 + 重要性 + 访问频率决定推送内容 |
| Day 18 | 知识关联发现 | 实现跨笔记的语义关联检测 |
| Day 19 | 推送输出 | 实现命令行推送通知（后期可扩展为微信/邮件） |
| Day 20 | 推送管理 | 实现"已读/稍后提醒/忽略"的反馈机制 |
| Day 21 | 集成测试 | 测试"入库 → 遗忘 → 推送 → 用户反馈"完整流程 |

**Week 3 验收标准：**

```
📢 [每日提醒] 你有2个知识点需要复习：
  1. 🔴 Redis LRU 策略（已学3天，未复习）
  2. 🟡 Python GIL（已学5天，复习1次）

📢 [知识关联] 你刚存的「秒杀架构」和之前的「Redis 缓存」
   有很强的关联，要查看分析吗？
```

### Week 4：打磨和演示

| 天数 | 任务 | 具体内容 |
|------|------|---------|
| Day 22 | Streamlit 界面 | 实现基础 Web 聊天界面 |
| Day 23 | 界面增强 | 添加知识库浏览、笔记详情展示 |
| Day 24 | 边界处理 | API 超时重试、空结果处理、异常恢复 |
| Day 25 | 性能优化 | 大文件处理、批量向量化、检索速度优化 |
| Day 26 | 数据导出 | 支持导出知识库为 Markdown 文件 |
| Day 27 | 录制演示 | 录制产品演示视频（3-5分钟） |
| Day 28 | 文档编写 | 写 README、架构说明文档 |
| Day 29 | 最终测试 | 全流程回归测试 |
| Day 30 | 交付 | 整理代码、清理注释、最终提交 |

---

## 项目结构

```
second-brain-agent/
├── README.md                    # 项目说明
├── .env.example                 # 环境变量模板
├── requirements.txt             # Python 依赖
├── main.py                      # 程序入口
├── config.py                    # 配置管理
│
├── agent/                       # Agent 核心模块
│   ├── __init__.py
│   ├── core.py                  # Agent Loop 实现
│   ├── prompt.py                # System Prompt 定义
│   └── llm.py                   # LLM 调用封装
│
├── tools/                       # 工具模块
│   ├── __init__.py
│   ├── add_knowledge.py         # 知识入库工具
│   ├── search_knowledge.py      # 知识检索工具
│   ├── manage_knowledge.py      # 知识管理工具（列表/删除/更新）
│   └── reminder.py              # 提醒推送工具
│
├── memory/                      # 记忆模块
│   ├── __init__.py
│   ├── short_term.py            # 短期记忆（对话历史）
│   └── long_term.py             # 长期记忆（用户偏好、知识图谱）
│
├── storage/                     # 存储模块
│   ├── __init__.py
│   ├── vector_store.py          # ChromaDB 向量存储
│   ├── document_parser.py       # 文档解析（TXT/MD）
│   └── metadata_store.py        # 元数据存储（JSON/SQLite）
│
├── scheduler/                   # 调度模块
│   ├── __init__.py
│   ├── scanner.py               # 知识库定时扫描
│   └── forgetting_curve.py      # 遗忘曲线算法
│
├── ui/                          # 界面模块
│   ├── __init__.py
│   ├── cli.py                   # 命令行界面
│   └── web.py                   # Streamlit Web 界面
│
├── data/                        # 数据目录
│   ├── notes/                   # 用户笔记存放目录
│   ├── chroma_db/               # ChromaDB 持久化目录
│   └── memory/                  # 记忆数据目录
│       ├── short_term.json      # 对话历史
│       └── long_term.json       # 用户偏好
│
└── tests/                       # 测试
    ├── test_tools.py
    ├── test_memory.py
    └── test_agent.py
```

---

## 核心模块设计

### 模块一：Agent 核心（agent/core.py）

```python
"""
Agent 核心循环实现（ReAct 模式）
"""

class SecondBrainAgent:
    def __init__(self, llm, tools, memory):
        self.llm = llm                    # LLM 引擎
        self.tools = tools                # 可用工具列表
        self.memory = memory              # 记忆系统
        self.max_iterations = 5           # 最大循环次数（防止死循环）

    def run(self, user_input: str) -> str:
        """Agent 主循环"""
        # 1. 将用户输入加入对话历史
        self.memory.add_message("user", user_input)

        # 2. 构建包含历史的 prompt
        messages = self.memory.get_messages()

        # 3. ReAct 循环
        for i in range(self.max_iterations):
            # LLM 决策：直接回答 or 调用工具
            response = self.llm.chat(
                messages=messages,
                tools=self.tools.get_schemas()
            )

            # 如果 LLM 选择直接回答
            if response.content:
                self.memory.add_message("assistant", response.content)
                return response.content

            # 如果 LLM 选择调用工具
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    # 执行工具
                    result = self.tools.execute(
                        tool_call.name,
                        tool_call.arguments
                    )
                    # 将工具结果加入对话
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

        return "抱歉，处理过程中出现了问题，请重试。"
```

### 模块二：文档解析（storage/document_parser.py）

```python
"""
文档解析与分块
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentParser:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,           # 每块最大500字符
            chunk_overlap=50,         # 块之间重叠50字符（保持语义连续）
            separators=["\n\n", "\n", "。", "！", "？"]
        )

    def parse_file(self, file_path: str) -> list[dict]:
        """解析文件并分块"""
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分块
        chunks = self.splitter.split_text(content)

        # 附带元数据
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })

        return documents

    def parse_text(self, text: str, source: str = "user_input") -> list[dict]:
        """解析纯文本输入"""
        chunks = self.splitter.split_text(text)
        return [
            {
                "content": chunk,
                "metadata": {
                    "source": source,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            }
            for i, chunk in enumerate(chunks)
        ]
```

### 模块三：向量存储（storage/vector_store.py）

```python
"""
ChromaDB 向量存储管理
"""

import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, persist_dir: str = "./data/chroma_db"):
        # 初始化 ChromaDB（持久化模式）
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )

    def add(self, documents: list[dict]):
        """批量添加文档到向量库"""
        self.collection.add(
            documents=[doc["content"] for doc in documents],
            ids=[f"doc_{hash(doc['content'])}" for doc in documents],
            metadatas=[doc["metadata"] for doc in documents]
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """语义检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        # 格式化结果
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]

    def count(self) -> int:
        """返回知识库中的文档总数"""
        return self.collection.count()
```

### 模块四：遗忘曲线（scheduler/forgetting_curve.py）

```python
"""
基于间隔重复的遗忘曲线算法
"""

import math
import json
from datetime import datetime, timedelta

class ForgettingCurve:
    def __init__(self, memory_file: str = "./data/memory/forgetting.json"):
        self.memory_file = memory_file
        self.records = self._load()

    def _load(self) -> dict:
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def record_access(self, note_id: str):
        """记录一次访问/复习"""
        now = datetime.now().isoformat()

        if note_id not in self.records:
            self.records[note_id] = {
                "first_seen": now,
                "access_count": 0,
                "review_dates": [],
                "difficulty": 1.0
            }

        record = self.records[note_id]
        record["access_count"] += 1
        record["review_dates"].append(now)

        # 每次复习后，根据间隔调整难度因子（SM-2 算法简化版）
        if len(record["review_dates"]) >= 2:
            prev = datetime.fromisoformat(record["review_dates"][-2])
            curr = datetime.fromisoformat(record["review_dates"][-1])
            interval = (curr - prev).days

            if interval < 2:
                record["difficulty"] = max(1.0, record["difficulty"] + 0.1)
            elif interval > 7:
                record["difficulty"] = max(1.0, record["difficulty"] - 0.1)

        self._save()

    def calculate_retention(self, note_id: str) -> float:
        """计算当前记忆保留率（0-1）"""
        if note_id not in self.records:
            return 0.0

        record = self.records[note_id]
        last_review = datetime.fromisoformat(record["review_dates"][-1])
        days_since = (datetime.now() - last_review).days

        # 遗忘曲线公式: R = e^(-t/S)
        # R: 保留率, t: 时间, S: 稳定性因子
        stability = record["difficulty"] * (record["access_count"] + 1)
        retention = math.exp(-days_since / (stability * 7))

        return round(min(1.0, max(0.0, retention)), 2)

    def get_notes_for_review(self, threshold: float = 0.5) -> list[dict]:
        """获取需要复习的笔记列表"""
        reminders = []

        for note_id, record in self.records.items():
            retention = self.calculate_retention(note_id)
            days_since = (datetime.now() - datetime.fromisoformat(
                record["review_dates"][-1]
            )).days

            if retention < threshold:
                # 计算优先级
                priority = (1 - retention) * record["access_count"]

                reminders.append({
                    "note_id": note_id,
                    "retention": retention,
                    "days_since_review": days_since,
                    "review_count": record["access_count"],
                    "priority": priority,
                    "urgency": self._get_urgency(retention, days_since)
                })

        # 按优先级排序
        reminders.sort(key=lambda x: x["priority"], reverse=True)
        return reminders

    def _get_urgency(self, retention: float, days: int) -> str:
        if retention < 0.2 or days > 14:
            return "🔴 紧急"
        elif retention < 0.4 or days > 7:
            return "🟡 重要"
        else:
            return "🟢 一般"
```

---

## Agent 工作流程

### 流程一：用户添加知识

```
用户输入："今天学了 Python 的 GIL 全局解释器锁，它会导致
          多线程在 CPU 密集型任务中无法真正并行"

Agent 思考：用户想要保存一条学习笔记

Agent 行动：调用 add_knowledge
  ├── 参数：{
  │     "content": "Python 的 GIL 全局解释器锁...",
  │     "tags": ["Python", "GIL", "多线程", "并发"],
  │     "importance": "high"
  │   }
  ├── 执行：文档解析 → 分块 → 向量化 → 存入 ChromaDB
  └── 记录：更新遗忘曲线，记录首次学习时间

Agent 回复："✅ 已保存！我给这条笔记打了标签：
            Python / GIL / 多线程 / 并发
            这是个重要概念，3天后我会提醒你复习。"
```

### 流程二：用户搜索知识

```
用户输入："我之前学过什么关于缓存的内容？"

Agent 思考：用户想搜索知识库，我需要调用搜索工具

Agent 行动：调用 search_knowledge
  ├── 参数：{"query": "缓存", "top_k": 5}
  ├── 执行：query 向量化 → ChromaDB 检索 → 返回 top-5
  └── 结果：找到3条相关笔记

Agent 思考：找到了结果，我需要用 LLM 总结后呈现

Agent 回复："你有3条关于缓存的笔记：
  1. 📄 Redis LRU 淘汰策略（4月12日）
     核心内容：LRU 会淘汰最近最少使用的键...
  2. 📄 MySQL 查询缓存的失效机制（4月15日）
     核心内容：当表数据更新时，该表的所有缓存失效...
  3. 📄 CDN 缓存与浏览器缓存（4月20日）
     核心内容：强缓存 vs 协商缓存...

  需要我详细展开某一条，或者帮你对比分析吗？"
```

### 流程三：Agent 主动推送

```
[每日定时任务触发] 扫描知识库

Agent 思考：检查所有笔记的遗忘曲线状态

Agent 执行：
  ├── 计算每条笔记的保留率
  ├── 筛选出保留率 < 0.5 的笔记
  └── 按优先级排序

Agent 决策：推送以下内容

📢 知识提醒（每日）：

🔴 紧急复习（1条）：
  「Python GIL 全局解释器锁」
   已学3天，未复习，保留率仅35%
   核心要点：GIL 导致多线程无法利用多核 CPU...
   [立即复习] [明天再看]

🟡 建议复习（2条）：
  「Redis LRU 淘汰策略」
   已学7天，复习1次，保留率58%
   [查看详情]

💡 知识关联（1条）：
  你刚存的「Python GIL」和之前的「多线程编程」笔记
  有关联——GIL 正是 Python 多线程的性能瓶颈所在。
  要我把这个关联整理出来吗？
```

---

## 记忆系统设计

### 短期记忆（memory/short_term.py）

```python
"""
对话历史管理 —— 短期记忆
"""

class ShortTermMemory:
    def __init__(self, max_messages: int = 50):
        self.messages = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

        # 超出窗口时，保留 System Prompt + 最近的消息
        if len(self.messages) > self.max_messages:
            # 保留前10条（可能是重要上下文）+ 最近30条
            self.messages = self.messages[:10] + self.messages[-30:]

    def get_messages(self) -> list[dict]:
        return self.messages

    def clear(self):
        self.messages = []
```

### 长期记忆（memory/long_term.py）

```python
"""
用户偏好与知识图谱 —— 长期记忆
"""

import json

class LongTermMemory:
    def __init__(self, memory_file: str = "./data/memory/long_term.json"):
        self.memory_file = memory_file
        self.data = self._load()

    def _load(self) -> dict:
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "user_preferences": {
                    "favorite_topics": [],       # 常关注的主题
                    "learning_pace": "normal",   # 学习节奏
                    "notification_time": "09:00" # 推送时间偏好
                },
                "knowledge_graph": {
                    "topics": {},                # 主题及其关联
                    "notes": {}                  # 笔记元数据
                }
            }

    def _save(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def update_preference(self, key: str, value):
        self.data["user_preferences"][key] = value
        self._save()

    def add_note_metadata(self, note_id: str, metadata: dict):
        self.data["knowledge_graph"]["notes"][note_id] = metadata
        self._save()

    def get_context_for_prompt(self) -> str:
        """生成用于 LLM prompt 的上下文摘要"""
        prefs = self.data["user_preferences"]
        notes_count = len(self.data["knowledge_graph"]["notes"])

        return f"""
用户偏好：
- 常关注主题：{', '.join(prefs['favorite_topics']) or '暂无'}
- 学习节奏：{prefs['learning_pace']}
- 知识库中共有 {notes_count} 条笔记
"""
```

---

## 主动推送机制

### 定时扫描器（scheduler/scanner.py）

```python
"""
每日定时扫描 —— 触发主动推送
"""

from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.forgetting_curve import ForgettingCurve

class KnowledgeScanner:
    def __init__(self, agent, forgetting_curve: ForgettingCurve):
        self.agent = agent
        self.forgetting_curve = forgetting_curve
        self.scheduler = BackgroundScheduler()

    def start(self, hour: int = 9, minute: int = 0):
        """启动定时任务（每天指定时间执行）"""
        self.scheduler.add_job(
            self.daily_scan,
            'cron',
            hour=hour,
            minute=minute
        )
        self.scheduler.start()
        print(f"⏰ 每日扫描已启动，将在每天 {hour:02d}:{minute:02d} 执行")

    def daily_scan(self):
        """每日扫描逻辑"""
        # 1. 获取需要复习的笔记
        reminders = self.forgetting_curve.get_notes_for_review(threshold=0.5)

        # 2. 获取知识关联
        recent_notes = self._get_recent_notes(days=1)
        associations = self._find_associations(recent_notes)

        # 3. 生成推送内容
        if reminders or associations:
            message = self._build_notification(reminders, associations)
            # 4. 输出推送（CLI 模式直接打印）
            print(f"\n{'='*50}")
            print(f"📢 每日知识提醒")
            print(f"{'='*50}")
            print(message)

    def _find_associations(self, recent_notes: list) -> list:
        """发现新旧笔记之间的关联"""
        associations = []
        # 用向量检索找到语义相近但不同的笔记
        # （实现略，核心是余弦相似度 > 阈值但 < 极高值）
        return associations

    def _build_notification(self, reminders, associations) -> str:
        """构建推送消息"""
        lines = []
        for r in reminders[:5]:  # 最多推5条
            lines.append(f"  {r['urgency']} {r['note_id']}")
            lines.append(f"     已学{r['days_since_review']}天，"
                        f"保留率{r['retention']*100:.0f}%")
        return "\n".join(lines)
```

---

## Prompt 设计

### System Prompt（agent/prompt.py）

```python
SYSTEM_PROMPT = """
你是一个个人知识管理 Agent，名叫"第二大脑"。你的核心能力：

## 你的工具
1. add_knowledge: 当用户想要保存笔记、记录学习内容时使用
2. search_knowledge: 当用户询问"我学过XX吗"、"找一下关于XX的内容"时使用
3. list_notes: 当用户想查看知识库概览时使用
4. delete_notes: 当用户想删除某条笔记时使用
5. send_reminder: 当需要推送复习提醒时使用

## 你的行为规则
- 用户说想要保存内容时，主动调用 add_knowledge
- 用户提问时，先判断是否需要搜索知识库
  - 如果是知识相关问题 → 先调用 search_knowledge，再基于结果回答
  - 如果是闲聊/通用问题 → 直接回答，不调用工具
- 回答时始终标注信息来源（哪条笔记、什么时间记录的）
- 语气友好、简洁，不要过度解释

## 你的记忆
- 你记得用户的所有对话历史
- 你记得用户的知识库内容
- 你记得用户的学习偏好

## 输出格式
- 列表类信息用编号
- 重要信息用 **加粗** 标注
- 需要用户决策时提供选项
"""
```

---

## 避坑指南

### 坑一：一上来就做 Web 界面

```
❌ 错误做法：花一周时间搭 Streamlit 界面，再开始写核心逻辑
✅ 正确做法：前3周纯命令行，确保核心功能正确后再加界面
```

**理由：** 界面开发会消耗大量时间，且如果核心逻辑有 bug，界面再好看也没用。命令行能让你专注在 Agent 逻辑上。

### 坑二：试图支持所有文件格式

```
❌ 错误做法：一开始就支持 PDF、DOCX、HTML、图片...
✅ 正确做法：MVP 只支持 .txt 和 .md，后期按需扩展
```

**理由：** PDF 解析（尤其是中文 PDF）是一个独立的大坑，需要处理字体嵌入、表格、图片等。DOCX 也类似。先把核心流程跑通。

### 坑三：用太复杂的框架

```
❌ 错误做法：用 LangChain 的 Agent/Chain/Memory 全家桶
✅ 正确做法：核心逻辑自己写，只用 LangChain 的工具类（DocumentLoader, TextSplitter）
```

**理由：** LangChain 的抽象层太多，出了问题很难调试。作为新手，理解底层原理比用框架更重要。Agent Loop 自己写，只需要50行代码。

### 坑四：忽略错误处理

```
❌ 错误做法：API 调用裸写，不处理异常
✅ 正确做法：从 Day 1 就写 try-except + 重试逻辑
```

**理由：** OpenAI API 会超时、会限流、会返回格式错误。如果不处理，调试时会浪费大量时间在"到底是 API 问题还是我的代码问题"上。

```python
# 从 Day 1 就养成这个习惯
import time

def call_llm_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
        except openai.RateLimitError:
            wait = 2 ** attempt
            print(f"API 限流，等待 {wait} 秒后重试...")
            time.sleep(wait)
        except openai.APIError as e:
            print(f"API 错误: {e}")
            if attempt == max_retries - 1:
                raise
```

### 坑五：追求 100% 检索准确率

```
❌ 错误做法：反复调参，追求向量检索的完美准确率
✅ 正确做法：先做到"大致对"，通过用户反馈迭代优化
```

**理由：** 语义检索本身就有模糊性（"缓存"能检索到"Redis"也能检索到"CDN"），这是正常的。过度调参会陷入局部最优。

### 坑六：一次写完所有模块

```
❌ 错误做法：设计完所有模块再开始编码
✅ 正确做法：每周只聚焦一个模块，写完测试通过再进下一个
```

**理由：** 新手最大的风险是"设计了很完美的架构，但什么都跑不起来"。每周有可验证的产出，才能保持动力和发现错误。

---

## 学习收获

做完这个项目后，你将掌握的 Agent 开发核心知识：

| 概念 | 在本项目中的实践 | 掌握程度 |
|------|-----------------|---------|
| Tool Calling | 定义工具 Schema，让 LLM 自动选择和调用 | 独立实现 |
| Prompt Engineering | System Prompt 设计、角色定义、输出格式控制 | 深入理解 |
| Agent Loop (ReAct) | 思考 → 行动 → 观察的完整循环 | 独立实现 |
| RAG | 检索增强生成的完整链路 | 深入理解 |
| 向量数据库 | ChromaDB 的使用和原理 | 基本掌握 |
| 短期记忆 | 对话历史管理、Context Window 控制 | 独立实现 |
| 长期记忆 | 用户偏好存储、知识图谱 | 基本掌握 |
| 定时任务 | APScheduler 的使用 | 掌握 |
| 错误处理 | API 重试、异常恢复、边界 case | 养成习惯 |
| 项目架构 | 模块化设计、关注点分离 | 刻意练习 |

### 这个项目可以写在简历上吗？

**可以。** 它展示了：
1. 你理解 Agent 的核心概念（不只是会调 API）
2. 你有完整的产品思维（从需求到实现到演示）
3. 你有独立开发能力（一个人 + AI 辅助完成）
4. 你有创新思维（主动推送 + 知识关联）

---

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-username/second-brain-agent.git
cd second-brain-agent

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 OpenAI API Key

# 5. 启动
python main.py
```

---

> **项目理念：** 知识的价值不在于存储，而在于在正确的时间被想起。让 AI 成为你的第二大脑，帮你在遗忘之前抓住那些重要的想法。
