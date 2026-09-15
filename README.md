# 第二大脑 - 个人知识管理 Agent

基于 ReAct 模式的智能知识管理助手，支持知识图谱、遗忘曲线、多跳推理。

## 快速开始（3步）

### 第一步：安装环境
双击 `setup.bat`，自动创建虚拟环境并安装依赖。

### 第二步：配置 API Key
1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env`，填入以下内容：

```
OPENAI_API_KEY=你的DeepSeek密钥
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-v4-flash
EMBEDDING_MODEL=text-embedding-3-small
SUPABASE_URL=你的Supabase项目URL
SUPABASE_KEY=你的Supabase密钥
```

### 第三步：启动
双击 `start.bat`，浏览器自动打开 http://localhost:8501

## 获取 API Key

### DeepSeek（大模型）
1. 访问 https://platform.deepseek.com
2. 注册 → 创建 API Key → 复制

### Supabase（云数据库）
1. 访问 https://supabase.com
2. 注册 → 创建项目 → 复制 Project URL 和 anon key
3. 在 SQL Editor 中执行 `setup_supabase.sql` 创建数据表

## 功能列表

- 仪表盘：总览知识库状态
- 知识问答：与 Agent 对话，自动检索回答
- 导入笔记：支持文件上传、手动输入、网页抓取
- 笔记管理：查看、筛选、删除笔记
- 复习提醒：基于遗忘曲线的智能复习
- 知识图谱：LLM 实体抽取 + 多跳推理
- 学习路径：个性化学习推荐

## 常见问题

**Q: 启动报错怎么办？**
A: 确保已安装 Python 3.10+，且 `.env` 文件配置正确。

**Q: Supabase 表不存在？**
A: 在 Supabase 的 SQL Editor 中执行 `setup_supabase.sql`。

**Q: 知识图谱功能报错？**
A: 确保网络能访问 DeepSeek API，知识图谱需要调用 LLM 抽取实体。

## 接入智能体（MCP / REST / Skills）

Web 界面之外，本项目还提供两种外部接入方式，**共用同一套 `tools/*` 与数据库**。

### 1. 获取 API Token
**方式一（推荐，普通用户）**：登录网页 → 左侧「设置」→「🔑 接入智能体」→ 点「生成新 Token」→ 复制保存。
> 需在 `.env` 配置 `PUBLIC_BASE_URL`（如 `http://39.96.27.17:8000`），页面才会显示正确地址。

**方式二（命令行）**：
```bash
curl -X POST http://<host>:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"你的密码"}'
# -> {"status":"success","token":"sb_...","user_id":"...","email":"..."}
```

### 2. MCP（Claude Desktop / Claude Code / Cursor 等）
- 地址：`http(s)://<host>:8000/mcp`
- 鉴权：请求头 `Authorization: Bearer <token>`

Claude Code：
```bash
claude mcp add --transport http second-brain http://<host>:8000/mcp \
  --header "Authorization: Bearer sb_xxx"
```

Claude Desktop（`claude_desktop_config.json`）：
```json
{
  "mcpServers": {
    "second-brain": {
      "type": "http",
      "url": "http://<host>:8000/mcp",
      "headers": { "Authorization": "Bearer sb_xxx" }
    }
  }
}
```

暴露的 MCP 工具：`add_knowledge`、`search_knowledge`、`manage_knowledge`、`send_reminder`、`fetch_web_content`、`knowledge_graph`。

### 3. REST（小艺 / Coze / Dify 等 OpenAPI 插件）
- 业务：`POST /api/add_note`、`/api/search`、`/api/reminders`、`/api/manage`、`/api/fetch_web`、`/api/knowledge_graph`
- Token 管理：`GET /api/tokens`、`POST /api/tokens`、`DELETE /api/tokens/{id}`
- 健康检查：`GET /api/health`

### 4. Skills（Claude 系）
`skills/` 提供 `knowledge-capture`、`spaced-review`、`knowledge-graph` 三个技能（含 `SKILL.md` 与可直接调 REST 的脚本），告诉智能体「何时用哪个工具」。
