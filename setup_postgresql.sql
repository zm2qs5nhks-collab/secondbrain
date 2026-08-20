-- PostgreSQL 建表脚本
-- 在服务器上执行: psql -U secondbrain -d secondbrain -f setup_postgresql.sql

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW())
);

CREATE TABLE IF NOT EXISTS notes (
    id VARCHAR(50) PRIMARY KEY,
    preview TEXT NOT NULL,
    tags JSONB DEFAULT '[]',
    source VARCHAR(50) DEFAULT 'user_input',
    importance VARCHAR(20) DEFAULT 'normal',
    user_id UUID REFERENCES users(id),
    created_at DOUBLE PRECISION NOT NULL,
    last_accessed DOUBLE PRECISION NOT NULL,
    access_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS note_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding FLOAT8[],
    user_id UUID REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS forgetting (
    id SERIAL PRIMARY KEY,
    note_id VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id),
    first_seen DOUBLE PRECISION NOT NULL,
    access_count INTEGER DEFAULT 1,
    review_dates JSONB DEFAULT '[]',
    difficulty DOUBLE PRECISION DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS user_prefs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL,
    value JSONB,
    user_id UUID REFERENCES users(id),
    UNIQUE(key, user_id)
);

CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(100) NOT NULL,
    related_notes JSONB DEFAULT '[]',
    count INTEGER DEFAULT 1,
    user_id UUID REFERENCES users(id),
    UNIQUE(topic, user_id)
);

CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_user ON note_embeddings(user_id);
CREATE INDEX IF NOT EXISTS idx_forgetting_user ON forgetting(user_id);
CREATE INDEX IF NOT EXISTS idx_forgetting_note ON forgetting(note_id);
