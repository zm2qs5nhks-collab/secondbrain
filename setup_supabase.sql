-- ============================================
-- 第二大脑 Supabase 数据库初始化 SQL
-- 在 Supabase 控制台 > SQL Editor 中执行一次
-- ============================================

-- 1. 笔记元数据表
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    preview TEXT NOT NULL DEFAULT '',
    tags JSONB DEFAULT '[]',
    source TEXT DEFAULT 'user_input',
    importance TEXT DEFAULT 'normal',
    created_at DOUBLE PRECISION DEFAULT 0,
    last_accessed DOUBLE PRECISION DEFAULT 0,
    access_count INTEGER DEFAULT 0
);

-- 2. 向量嵌入表
CREATE TABLE IF NOT EXISTS note_embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding FLOAT8[]
);

-- 3. 遗忘曲线表
CREATE TABLE IF NOT EXISTS forgetting (
    note_id TEXT PRIMARY KEY,
    first_seen DOUBLE PRECISION DEFAULT 0,
    access_count INTEGER DEFAULT 0,
    review_dates FLOAT8[] DEFAULT '{}',
    difficulty FLOAT8 DEFAULT 1.0
);

-- 4. 用户偏好表
CREATE TABLE IF NOT EXISTS user_prefs (
    key TEXT PRIMARY KEY,
    value JSONB
);

-- 5. 主题/标签表
CREATE TABLE IF NOT EXISTS topics (
    topic TEXT PRIMARY KEY,
    related_notes JSONB DEFAULT '[]',
    count INTEGER DEFAULT 1
);

-- 启用 RLS（Row Level Security）— 可选，建议开启
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE forgetting ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_prefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;

-- 允许 anon key 访问（开发阶段用）
CREATE POLICY "Allow all for anon" ON notes FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON note_embeddings FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON forgetting FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON user_prefs FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON topics FOR ALL USING (true);
