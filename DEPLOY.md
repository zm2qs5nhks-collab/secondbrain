# 第二大脑 —— 部署指南

## 一、准备工作（约15分钟）

### 1. 注册 Supabase（云数据库）

1. 访问 [https://supabase.com](https://supabase.com)，用 GitHub 账号免费注册
2. 点击 **New Project**，填写项目名称和数据库密码
3. 等待1分钟创建完成
4. 进入项目后，点击左侧 **Settings** → **API**
5. 复制两个值：
   - **Project URL**（格式：`https://xxx.supabase.co`）
   - **anon public key**（格式：`eyJhbG...`开头的长字符串）

### 2. 初始化数据库表

1. 在 Supabase 控制台，点击左侧 **SQL Editor**
2. 点击 **New query**
3. 把 `setup_supabase.sql` 文件的内容粘贴进去
4. 点击 **Run** 执行
5. 看到 "Success" 表示表创建完成

### 3. 注册 GitHub

如果还没有 GitHub 账号，去 [https://github.com](https://github.com) 注册一个。

---

## 二、部署到 Streamlit Cloud（约10分钟）

### 步骤1：上传代码到 GitHub

1. 在 GitHub 上创建一个新仓库（Repository），名称随意，如 `second-brain-agent`
2. 把项目所有文件上传到这个仓库：

```bash
cd F:\the_first_idea
git init
git add .
git commit -m "second brain agent"
git remote add origin https://github.com/你的用户名/second-brain-agent.git
git branch -M main
git push -u origin main
```

### 步骤2：在 Streamlit Cloud 部署

1. 访问 [https://share.streamlit.io](https://share.streamlit.io)
2. 用 GitHub 账号登录
3. 点击 **New app**
4. 选择你的仓库 `second-brain-agent`
5. **Main file path** 填：`app.py`
6. 点击 **Advanced settings**
7. 在 **Secrets** 中填入以下内容（替换为你自己的值）：

```toml
OPENAI_API_KEY = "你的API Key"
OPENAI_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-v4-flash"
EMBEDDING_MODEL = "text-embedding-3-small"
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJhbG..."
```

8. 点击 **Deploy**

等待2-3分钟，部署完成后会给你一个网址，如：
`https://你的用户名-second-brain-agent-app-xxx.streamlit.app`

**把这个网址分享给任何人，他们打开就能用！**

---

## 三、本地调试

如果想在本地运行（需要先配置 .env 文件）：

```bash
cd F:\the_first_idea

# 安装依赖
pip install -r requirements.txt

# 启动图形界面
streamlit run app.py

# 或者启动命令行版本
python main.py
```

---

## 四、项目文件结构

```
second-brain-agent/
├── app.py                    # Streamlit 图形界面（入口）
├── main.py                   # 命令行版本入口
├── config.py                 # 配置管理
├── requirements.txt          # Python 依赖
├── setup_supabase.sql        # Supabase 建表 SQL
├── .env.example              # 环境变量模板
├── .streamlit/
│   └── config.toml           # Streamlit 配置
├── agent/                    # Agent 核心
│   ├── core.py               # ReAct 循环
│   ├── llm.py                # LLM 调用
│   └── prompt.py             # System Prompt
├── tools/                    # 工具模块
│   ├── add_knowledge.py      # 添加笔记
│   ├── search_knowledge.py   # 搜索笔记
│   ├── manage_knowledge.py   # 管理笔记
│   ├── reminder.py           # 复习提醒
│   └── fetch_web.py          # 网页抓取
├── storage/                  # 云端存储
│   ├── db.py                 # Supabase 连接
│   ├── vector_store.py       # 向量搜索
│   ├── metadata_store.py     # 笔记元数据
│   └── document_parser.py    # 文档解析
├── memory/                   # 记忆系统
│   ├── short_term.py         # 对话历史
│   └── long_term.py          # 用户偏好
└── scheduler/                # 调度系统
    └── forgetting_curve.py   # 遗忘曲线
```

---

## 五、常见问题

**Q: 部署后打开网页报错？**
A: 检查 Streamlit Cloud 的 Secrets 是否配置正确，特别是 SUPABASE_URL 和 SUPABASE_KEY。

**Q: 笔记搜索不准？**
A: 确保你的 API 支持 Embedding 调用。DeepSeek 目前不支持 Embedding，建议使用 OpenAI 或智谱AI的 Embedding 接口。可以在 .env 中单独设置 `EMBEDDING_MODEL`。

**Q: 网页抓取失败？**
A: 部分网站有反爬机制，这是正常的。可以在浏览器中先确认URL能正常打开。

**Q: 数据会丢失吗？**
A: 不会。所有数据存储在 Supabase 云端，只要不删除 Supabase 项目，数据永久保存。
